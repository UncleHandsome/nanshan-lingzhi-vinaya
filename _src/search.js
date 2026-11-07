/* 全站全文搜尋 v1：目錄捷徑、漸進載入、競態保護、特殊字元安全 */
(function () {
  'use strict';

  var input = document.getElementById('q');
  if (!input) return;

  var hitsEl = document.getElementById('hits');
  var quickEl = document.getElementById('quickhits');
  var countEl = document.getElementById('count');
  var statusEl = document.getElementById('searchstatus');
  var errorEl = document.getElementById('searcherror');
  var bookFilter = document.getElementById('bookfilter');
  var navTree = document.getElementById('navtree');
  var BOOKS = window.SEARCH_BOOKS || [];
  var loaded = {};
  var loading = {};
  var navData = null;
  var querySeq = 0;
  var currentQuery = '';
  var currentTerms = [];
  var activeIndex = -1;
  var timer = null;
  var navVersion = navTree ? (navTree.getAttribute('data-nav-version') || '11') : '11';

  function norm(s) {
    return String(s || '').toLocaleLowerCase();
  }

  function esc(s) {
    return String(s || '').replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function escRe(s) {
    return String(s).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  function highlight(text, terms) {
    var t = String(text || '');
    if (!terms.length) return esc(t);
    var re = new RegExp('(' + terms.map(escRe).join('|') + ')', 'gi');
    var out = '', last = 0, m;
    while ((m = re.exec(t)) !== null) {
      out += esc(t.slice(last, m.index)) + '<mark>' + esc(m[0]) + '</mark>';
      last = m.index + m[0].length;
      if (m.index === re.lastIndex) re.lastIndex++;
    }
    return out + esc(t.slice(last));
  }

  function snippet(text, terms, length) {
    var t = String(text || '');
    if (!terms.length) return esc(t.slice(0, length));
    var lower = norm(t), pos = -1;
    terms.forEach(function (term) {
      var i = lower.indexOf(norm(term));
      if (i >= 0 && (pos < 0 || i < pos)) pos = i;
    });
    if (pos < 0) pos = 0;
    var start = Math.max(0, pos - 30);
    var end = Math.min(t.length, start + length);
    return (start > 0 ? '…' : '') + highlight(t.slice(start, end), terms) + (end < t.length ? '…' : '');
  }

  function score(entry, terms, phrase) {
    var o = norm(entry.o), t = norm(entry.t), v = norm(entry.v);
    var s = 0;
    if (o.indexOf(phrase) === 0) s += 12;
    if (o.indexOf(phrase) >= 0) s += 7;
    if (t.indexOf(phrase) >= 0) s += 3;
    if (v.indexOf(phrase) >= 0) s += 5;
    terms.forEach(function (term) {
      if (o.indexOf(term) === 0) s += 4;
      else if (o.indexOf(term) >= 0) s += 2;
      if (t.indexOf(term) >= 0) s += 1;
      if (v.indexOf(term) >= 0) s += 1;
    });
    return s;
  }

  function matches(entry, terms) {
    var hay = norm(entry.o) + '\n' + norm(entry.t) + '\n' + norm(entry.v);
    for (var i = 0; i < terms.length; i++) {
      if (hay.indexOf(terms[i]) < 0) return false;
    }
    return true;
  }

  function loadBook(book) {
    if (loaded[book.id]) return Promise.resolve(loaded[book.id]);
    if (loading[book.id]) return loading[book.id];
    loading[book.id] = new Promise(function (resolve, reject) {
      var s = document.createElement('script');
      s.src = book.file;
      s.async = true;
      s.onload = function () {
        var data = window.SIDX && window.SIDX[book.id];
        if (!data) { reject(new Error('索引格式錯誤：' + book.title)); return; }
        loaded[book.id] = data;
        resolve(data);
      };
      s.onerror = function () { reject(new Error('索引載入失敗：' + book.title)); };
      document.head.appendChild(s);
    });
    return loading[book.id];
  }

  function loadNav() {
    if (navData) return Promise.resolve(navData);
    return fetch('nav.json?v=' + navVersion, { cache: 'no-cache' })
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(function (d) { navData = d; return d; })
      .catch(function () { return null; });
  }

  function setUrl(q) {
    if (!history.replaceState) return;
    var base = location.pathname;
    // file:// 或沙箱環境呼叫 replaceState 會丟 SecurityError，不能讓它中斷搜尋
    try {
      history.replaceState(null, '', q ? base + '?q=' + encodeURIComponent(q) : base);
    } catch (e) {}
  }

  function getQuery() {
    try {
      return new URLSearchParams(location.search).get('q') || '';
    } catch (e) {
      var m = location.search.match(/[?&]q=([^&]*)/);
      if (!m) return '';
      try { return decodeURIComponent(m[1].replace(/\+/g, ' ')); }
      catch (err) { return ''; }
    }
  }

  function quickResults(q) {
    if (!navData || !q) return [];
    var out = [], needle = norm(q);
    var only = bookFilter ? bookFilter.value : '';
    (navData.books || []).forEach(function (book) {
      if (out.length >= 8) return;
      if (only && book.out !== only) return;   // 跟「限定書籍」保持一致
      if (norm(book.title).indexOf(needle) >= 0) {
        var first = (book.vols || [])[0];
        if (first) out.push({ bid: book.out, v: first.v, i: '', title: book.title, kind: '書' });
      }
      (book.vols || []).forEach(function (vol) {
        if (out.length >= 8) return;
        if (norm(vol.v).indexOf(needle) >= 0) {
          out.push({ bid: book.out, v: vol.v, i: '', title: book.title + '　' + vol.v, kind: '卷' });
        }
        (vol.secs || []).forEach(function (sec) {
          if (out.length >= 8) return;
          if (norm(sec[1]).indexOf(needle) >= 0) {
            out.push({ bid: book.out, v: vol.v, i: sec[0], title: sec[1], kind: '篇' });
          }
        });
      });
    });
    return out;
  }

  function renderQuick(q, terms) {
    if (!quickEl) return;
    var items = quickResults(q);
    if (!items.length) { quickEl.innerHTML = ''; quickEl.hidden = true; return; }
    var html = '<h2 class="quicktitle">篇目捷徑</h2><div class="quicklist">';
    items.forEach(function (x) {
      var href = x.bid + '/' + x.v + '.html' + (x.i ? '#' + x.i : '');
      html += '<a class="quickhit" href="' + href + '"><span class="qkind">' + esc(x.kind) + '</span>' +
        '<span class="qtext">' + highlight(x.title, terms) + '</span></a>';
    });
    quickEl.innerHTML = html + '</div>';
    quickEl.hidden = false;
  }

  function renderResults(results, q, terms, elapsed, failed) {
    if (!hitsEl) return;
    if (!results.length) {
      hitsEl.innerHTML = '<div class="empty">查無「' + esc(q) + '」。可試：' +
        '<a href="?q=羯磨">羯磨</a>、<a href="?q=波羅夷">波羅夷</a>、' +
        '<a href="?q=安居">安居</a>，或較短的關鍵字。</div>';
      if (countEl) countEl.textContent = '沒有結果';
      if (statusEl) statusEl.textContent = '沒有結果';
      return;
    }
    var total = results.length;
    results.sort(function (a, b) { return b.sc - a.sc || a.order - b.order; });
    var byBook = {};
    results.forEach(function (r) {
      (byBook[r.bid] = byBook[r.bid] || []).push(r);
    });
    var perBook = (bookFilter && bookFilter.value) ? 300 : Math.max(30, Math.floor(300 / Math.max(1, BOOKS.length)));
    var shown = 0;
    var frag = document.createDocumentFragment();
    BOOKS.forEach(function (book) {
      var arr = byBook[book.id];
      if (!arr || !arr.length) return;
      var h = document.createElement('h3');
      h.className = 'hitbook';
      h.textContent = book.title + '（' + arr.length + '）';
      frag.appendChild(h);
      arr.slice(0, perBook).forEach(function (x) {
        var a = document.createElement('a');
        a.className = 'hit';
        a.href = x.bid + '/' + x.v + '.html' + (x.i ? '#' + x.i : '');
        a.innerHTML = '<div class="meta">' + esc(x.v) + '　<span>前往 →</span></div>' +
          '<div class="o">' + snippet(x.o, terms, 110) + '</div>' +
          '<div class="t">' + snippet(x.t, terms, 110) + '</div>';
        frag.appendChild(a);
        shown++;
      });
    });
    hitsEl.innerHTML = '';
    hitsEl.appendChild(frag);
    activeIndex = -1;
    var note = failed ? '（' + failed + ' 本書索引載入失敗）' : '';
    var cap = shown < total ? '（顯示 ' + shown + ' 筆）' : '';
    if (countEl) countEl.textContent = '找到 ' + total + ' 筆' + cap + note + '　·　' + elapsed + ' ms';
    if (statusEl) statusEl.textContent = '找到 ' + total + ' 筆結果' + note;
  }

  function setActive(i) {
    var hs = hitsEl ? hitsEl.querySelectorAll('.hit') : [];
    if (!hs.length) return;
    if (activeIndex >= 0 && hs[activeIndex]) hs[activeIndex].classList.remove('active');
    activeIndex = (i + hs.length) % hs.length;
    hs[activeIndex].classList.add('active');
    hs[activeIndex].scrollIntoView({ block: 'nearest' });
  }

  function run(q) {
    q = String(q || '').trim();
    currentQuery = q;
    currentTerms = q ? q.split(/\s+/).filter(Boolean) : [];
    var seq = ++querySeq;
    setUrl(q);
    if (errorEl) { errorEl.hidden = true; errorEl.innerHTML = ''; }
    if (!q) {
      if (hitsEl) hitsEl.innerHTML = '';
      if (quickEl) { quickEl.innerHTML = ''; quickEl.hidden = true; }
      if (countEl) countEl.textContent = '';
      if (statusEl) statusEl.textContent = '';
      return;
    }
    if (countEl) countEl.textContent = '搜尋中…';
    if (statusEl) statusEl.textContent = '搜尋中';
    if (hitsEl) hitsEl.innerHTML = '';
    loadNav().then(function () {
      if (seq !== querySeq) return;
      renderQuick(q, currentTerms);
    });
    var targets = BOOKS.filter(function (b) {
      return !bookFilter || !bookFilter.value || bookFilter.value === b.id;
    });
    if (!targets.length) {
      if (countEl) countEl.textContent = '沒有可搜尋的書籍';
      return;
    }
    var results = [];
    var failed = 0;
    var pending = targets.length;
    var started = Date.now();
    var order = 0;
    targets.forEach(function (book) {
      loadBook(book).then(function (data) {
        if (seq !== querySeq) return;
        (data.entries || []).forEach(function (e) {
          if (matches(e, currentTerms)) {
            results.push({
              bid: book.id, v: e.v, o: e.o, t: e.t, i: e.i || '',
              sc: score(e, currentTerms, norm(q)), order: order++
            });
          }
        });
        pending--;
        if (pending === 0) {
          renderResults(results, q, currentTerms, Date.now() - started, failed);
        } else if (statusEl) {
          statusEl.textContent = '已載入 ' + (targets.length - pending) + ' / ' + targets.length + ' 本書';
        }
      }).catch(function () {
        if (seq !== querySeq) return;
        delete loading[book.id];
        failed++;
        pending--;
        if (pending === 0) {
          if (!results.length && failed === targets.length) {
            if (countEl) countEl.textContent = '索引載入失敗';
            if (statusEl) statusEl.textContent = '索引載入失敗';
            if (errorEl) {
              errorEl.hidden = false;
              errorEl.innerHTML = '<span>無法載入搜尋索引。</span><button type="button" id="searchretry">重試</button>';
            }
          } else {
            renderResults(results, q, currentTerms, Date.now() - started, failed);
          }
        }
      });
    });
  }

  function init() {
    if (!BOOKS.length) {
      if (countEl) countEl.textContent = '搜尋索引清單載入失敗。';
      return;
    }
    var initial = getQuery();
    if (initial) {
      input.value = initial;
      run(initial);
    } else {
      loadNav();
    }
    input.addEventListener('input', function () {
      clearTimeout(timer);
      timer = setTimeout(function () { run(input.value); }, 180);
    });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); setActive(activeIndex + 1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); setActive(activeIndex - 1); }
      else if (e.key === 'Enter') {
        var a = hitsEl ? hitsEl.querySelector('.hit.active') : null;
        if (!a) a = hitsEl ? hitsEl.querySelector('.hit') : null;
        if (a) location.href = a.href;
      } else if (e.key === 'Escape') {
        input.value = '';
        run('');
        input.focus();
      }
    });
    if (bookFilter) bookFilter.addEventListener('change', function () { run(input.value); });
    if (errorEl) errorEl.addEventListener('click', function (e) {
      if (!e.target.closest || !e.target.closest('#searchretry')) return;
      loaded = {};
      loading = {};
      run(input.value);
    });
  }

  init();
})();
