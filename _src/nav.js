/* 側欄與全站導覽 v9：書 → 卷 → 篇 三層鑽取、跨書篩選、所在篇（scroll 推導）、
   閱讀模式（原文／白話／雙欄）、複製本段連結、抽屜、快捷鍵 */
(function () {
  'use strict';

  var box = document.getElementById('navtree');
  if (!box) return;

  var nav = document.getElementById('sidebar') || box.closest('nav');
  var root = box.getAttribute('data-root') || '';
  var version = box.getAttribute('data-nav-version') || '11';
  var path = safePath();
  var isMobileQuery = window.matchMedia ? window.matchMedia('(max-width: 1100px)') : null;
  var BOOK_KEY = 'dsh-nav-book-v3';
  var SCROLL_KEY = 'dsh-nav-scroll-v3:' + path;
  var DATA = null;
  var curBook = null;
  var openVol = null;
  var filter = null;
  var filterCount = null;
  var resultsEl = null;
  var bodyEl = null;
  var activeLink = null;
  var drawerOpen = false;
  var toggle = document.getElementById('navtoggle');
  var closeBtn = document.getElementById('navclose');
  var scrim = document.getElementById('navscrim');
  var siteSearch = document.getElementById('q');

  function safePath() {
    try { return decodeURIComponent(location.pathname); }
    catch (e) { return location.pathname; }
  }

  function readStr(key) {
    try { return localStorage.getItem(key) || ''; } catch (e) { return ''; }
  }

  function writeStr(key, value) {
    try { localStorage.setItem(key, value); } catch (e) {}
  }

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function norm(s) {
    return String(s || '').toLocaleLowerCase();
  }

  function isMobile() {
    return !!(isMobileQuery && isMobileQuery.matches);
  }

  // ── 篩選工具列 ─────────────────────────────────────────────
  function makeTools() {
    var tools = document.createElement('div');
    tools.className = 'navtools';
    tools.innerHTML =
      '<div class="navfilterwrap">' +
      '<input id="navfilter" type="search" placeholder="僅搜書名、卷名、篇名" autocomplete="off" ' +
      'title="只篩選目錄標題；要找經文內容請用全文搜尋" ' +
      'aria-label="篩選目錄（只搜書名、卷名、篇名）" aria-controls="navtree">' +
      '<span id="navfiltercount" class="navfiltercount" aria-live="polite"></span>' +
      '</div>';
    box.parentNode.insertBefore(tools, box);
    filter = document.getElementById('navfilter');
    filterCount = document.getElementById('navfiltercount');

    filter.addEventListener('input', applyFilter);
    filter.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        e.preventDefault();
        clearFilter();
        filter.blur();
      } else if (e.key === 'Enter') {
        var a = firstResult();
        if (a) { a.click(); filter.blur(); }
      } else if (e.key === 'ArrowDown') {
        var a2 = firstResult();
        if (a2) { e.preventDefault(); a2.focus(); }
      }
    });
  }

  function clearFilter() {
    if (!filter) return;
    filter.value = '';
    applyFilter();
  }

  function firstResult() {
    if (!resultsEl || resultsEl.hidden) return null;
    return resultsEl.querySelector('a[href]');
  }

  // ── 資料與渲染 ─────────────────────────────────────────────
  function bookOfPath() {
    if (!DATA) return '';
    for (var i = 0; i < DATA.books.length; i++) {
      if (path.indexOf('/' + DATA.books[i].out + '/') >= 0) return DATA.books[i].out;
    }
    return '';
  }

  function bookByOut(out) {
    if (!DATA) return null;
    for (var i = 0; i < DATA.books.length; i++) {
      if (DATA.books[i].out === out) return DATA.books[i];
    }
    return null;
  }

  function render() {
    var b = bookByOut(curBook) || (DATA.books || [])[0];
    if (!b) return;
    curBook = b.out;
    writeStr(BOOK_KEY, b.out);

    var html = '<p class="navgrouplabel">書目</p>' +
      '<details class="navbookpick"><summary><span class="bk">' + esc(b.title) +
      '</span></summary><ul>';
    (DATA.books || []).forEach(function (x) {
      html += '<li><button type="button" data-out="' + esc(x.out) + '"' +
        (x.out === b.out ? ' class="cur" aria-current="true"' : '') + '>' +
        esc(x.title) + '</button></li>';
    });
    html += '</ul></details>';

    html += '<div class="navvols">';
    var curVolName = '';
    (b.vols || []).forEach(function (v) {
      var isCurPage = path.indexOf('/' + b.out + '/' + v.v + '.html') >= 0;
      if (isCurPage) curVolName = v.v;
      var open = isCurPage || openVol === v.v;
      var n = (v.secs || []).length;
      html += '<details class="vol' + (isCurPage ? ' curpage' : '') + '"' + (open ? ' open' : '') +
        ' data-v="' + esc(v.v) + '">' +
        '<summary><span class="vname">' + esc(v.v) + '</span>' +
        '<span class="vcount">' + (n ? n + ' 篇' : '全卷') + '</span></summary><ul>' +
        '<li class="wholevol"><a href="' + root + b.out + '/' + v.v + '.html">全卷</a></li>';
      (v.secs || []).forEach(function (s) {
        var here = isCurPage && location.hash === '#' + s[0];
        html += '<li><a href="' + root + b.out + '/' + v.v + '.html#' + s[0] +
          '" title="' + esc(s[1]) + '"' +
          (here ? ' class="cursec" aria-current="location"' : '') + '>' + esc(s[1]) + '</a></li>';
      });
      html += '</ul></details>';
    });
    html += '</div>';

    bodyEl = document.createElement('div');
    bodyEl.className = 'navbody';
    bodyEl.innerHTML = html;

    resultsEl = document.createElement('div');
    resultsEl.className = 'navresults';
    resultsEl.hidden = true;

    box.innerHTML = '';
    box.appendChild(bodyEl);
    box.appendChild(resultsEl);

    bindBooks();
    bindVols();
    revealCurrent();
  }

  function bindBooks() {
    bodyEl.querySelectorAll('.navbookpick button').forEach(function (btn) {
      btn.addEventListener('click', function () {
        curBook = btn.getAttribute('data-out');
        openVol = null;
        render();
        if (filter) filter.value = '';
        var f = bodyEl.querySelector('.navbookpick');
        if (f) f.open = false;
        var s = bodyEl.querySelector('.navbookpick > summary');
        if (s) s.focus();
      });
    });
  }

  function bindVols() {
    bodyEl.querySelectorAll('details.vol').forEach(function (d) {
      d.addEventListener('toggle', function () {
        if (!d.open) return;
        bodyEl.querySelectorAll('details.vol[open]').forEach(function (o) {
          if (o !== d) o.open = false;
        });
        openVol = d.getAttribute('data-v');
      });
    });
  }

  // 把「所在篇」帶進視野；若使用者上次的側欄位置已還原則不打扰
  function revealCurrent() {
    if (!nav) return;
    var a = box.querySelector('a.cursec') ||
      box.querySelector('details.vol.curpage > summary');
    if (!a) return;
    var r = a.getBoundingClientRect();
    var nr = nav.getBoundingClientRect();
    if (r.top < nr.top + 110 || r.bottom > nr.bottom - 24) {
      nav.scrollTop += r.top - nr.top - 150;
    }
  }

  function restoreScroll() {
    if (!nav) return false;
    var top = 0;
    try { top = parseInt(sessionStorage.getItem(SCROLL_KEY) || '0', 10); } catch (e) {}
    nav.addEventListener('scroll', function () {
      try { sessionStorage.setItem(SCROLL_KEY, String(nav.scrollTop)); } catch (e) {}
    }, { passive: true });
    if (top > 0) { nav.scrollTop = top; return true; }
    return false;
  }

  // ── 篩選：跨書扁平結果 ─────────────────────────────────────
  function applyFilter() {
    if (!filter || !DATA) return;
    var q = norm(filter.value.trim());
    if (!q) {
      if (resultsEl) { resultsEl.hidden = true; resultsEl.innerHTML = ''; }
      if (bodyEl) bodyEl.hidden = false;
      if (filterCount) filterCount.textContent = '';
      return;
    }

    var groups = [], total = 0;
    (DATA.books || []).forEach(function (b) {
      var bookHit = norm(b.title).indexOf(q) >= 0;
      (b.vols || []).forEach(function (v) {
        var volHit = bookHit || norm(v.v).indexOf(q) >= 0;
        var items = (v.secs || []).filter(function (s) {
          return volHit || norm(s[1]).indexOf(q) >= 0;
        });
        if (items.length || (volHit && !(v.secs || []).length)) {
          groups.push({ b: b, v: v, items: items });
          total += items.length;
        }
      });
    });

    var html = '';
    var shown = 0;
    groups.forEach(function (g) {
      html += '<div class="navresgrp"><p class="navreshead"><span class="rb">' + esc(g.b.title) +
        '</span><span class="rv">' + esc(g.v.v) + '</span></p><ul>';
      if (!g.items.length) {
        html += '<li><a href="' + root + g.b.out + '/' + g.v.v + '.html">（全卷）</a></li>';
      }
      g.items.forEach(function (s) {
        if (shown >= 300) return;
        shown++;
        html += '<li><a href="' + root + g.b.out + '/' + g.v.v + '.html#' + s[0] +
          '" title="' + esc(s[1]) + '">' + esc(s[1]) + '</a></li>';
      });
      html += '</ul></div>';
    });
    if (!groups.length) {
      var qraw = filter.value.trim();
      html = '<p class="navempty">沒有符合「' + esc(qraw) + '」的篇名。' +
        '<br><a class="navempty-search" href="' + root + 'search.html?q=' +
        encodeURIComponent(qraw) + '">在全文搜尋「' + esc(qraw) + '」→</a></p>';
    }

    resultsEl.innerHTML = html;
    resultsEl.hidden = false;
    bodyEl.hidden = true;
    if (filterCount) {
      filterCount.textContent = total > 300 ? '300+' : (total ? total + ' 篇' : '無結果');
    }
  }

  // ── 所在篇高亮（scroll 位置推導，不用 IntersectionObserver）──────
  // 搜尋落地／快速跳轉會跳過中間所有節，IO 不會回報；直接用捲動位置
  // 找「最後一個在視窗頂端上方的 h2」，hash 落地與手動捲動都會正確。
  var heads = [];
  var headTops = [];
  var secLinks = {};
  var activeLink = null;
  var scrollTick = false;

  function collectHeads() {
    heads = [].slice.call(document.querySelectorAll('main h2.sec'));
    headTops = heads.map(function (h) {
      return h.getBoundingClientRect().top + window.pageYOffset;
    });
    secLinks = {};
    [].slice.call(box.querySelectorAll('a[href*="#p"]')).forEach(function (a) {
      var u;
      try { u = new URL(a.href, location.href); } catch (e) { return; }
      if (u.pathname !== location.pathname) return;
      var id = u.hash.slice(1);
      if (id) secLinks[id] = a;
    });
  }

  function setCurrent(a) {
    if (activeLink === a) return false;
    if (activeLink) {
      activeLink.classList.remove('cursec');
      activeLink.removeAttribute('aria-current');
    }
    activeLink = a || null;
    if (activeLink) {
      activeLink.classList.add('cursec');
      activeLink.setAttribute('aria-current', 'location');
    }
    return true;
  }

  function revealLink(a) {
    if (!nav || !a) return;
    var r = a.getBoundingClientRect();
    var nr = nav.getBoundingClientRect();
    if (r.top < nr.top + 110 || r.bottom > nr.bottom - 24) {
      nav.scrollTop += r.top - nr.top - 150;
    }
  }

  function syncCurrentByScroll() {
    if (!heads.length) return;
    var y = window.pageYOffset + topGap() + 8;
    var cur = null;
    for (var i = 0; i < heads.length; i++) {
      if (headTops[i] <= y) cur = secLinks[heads[i].id] || cur;
      else break;
    }
    // 在第一節之前（頁首 h1／byline 區）也先指向第一節，避免「目前位置」空白
    if (!cur && heads.length) cur = secLinks[heads[0].id] || null;
    if (setCurrent(cur) && cur) revealLink(cur);
  }

  function onScrollSpy() {
    if (scrollTick) return;
    scrollTick = true;
    (window.requestAnimationFrame || setTimeout)(function () {
      scrollTick = false;
      syncCurrentByScroll();
    }, 16);
  }

  function spy() {
    collectHeads();
    activeLink = box.querySelector('a.cursec') || null;
    if (activeLink) activeLink.classList.add('cursec');
    syncCurrentByScroll();
  }

  window.addEventListener('scroll', onScrollSpy, { passive: true });
  window.addEventListener('resize', function () {
    collectHeads();
    syncCurrentByScroll();
  }, { passive: true });

  // ── 錨點定位 ──────────────────────────────────────────────
  // 長卷（近百萬像素高）載入時版面未必已定稿，只對位一次會落在錯的位置；
  // 改成反覆校正到連續兩次一致為止。
  var jumpSeq = 0;
  var userMoved = false;

  window.addEventListener('wheel', function () { userMoved = true; }, { passive: true });
  window.addEventListener('touchstart', function () { userMoved = true; }, { passive: true });
  window.addEventListener('keydown', function (e) {
    if (/^(PageDown|PageUp|ArrowDown|ArrowUp|Home|End| )$/.test(e.key)) userMoved = true;
  });

  function topGap() {
    var bar = document.querySelector('.mobilebar');
    if (!bar) return 14;
    var cs = window.getComputedStyle(bar);
    if (cs.display === 'none' || cs.position !== 'fixed') return 14;
    return bar.getBoundingClientRect().height + 12;
  }

  // 搜尋索引的錨點有三種：
  //   u…     → 定稿 key 衍生的穩定 id（新索引；關 JS 也能原生跳轉）
  //   pair-N → main 裡第 N 個 .pair（舊索引；N 從 0 起算）
  //   sN     → 舊合編頁的位置錨點（N 從 1 起算；保留舊分享連結）
  function resolveAnchor(id) {
    var el = document.getElementById(id);
    if (el) return el;
    var m = /^pair-(\d+)$/.exec(id);
    if (m) {
      var list = document.querySelectorAll('main .pair');
      return list[parseInt(m[1], 10)] || null;
    }
    m = /^s(\d+)$/.exec(id);
    if (m) {
      var list2 = document.querySelectorAll('main .pair');
      return list2[parseInt(m[1], 10) - 1] || null;
    }
    return null;
  }

  var hitEl = null;
  function markHit(el) {
    if (!el) return;
    if (hitEl && hitEl !== el) hitEl.classList.remove('searchhit');
    if (!el.classList.contains('pair') && !el.classList.contains('sec')) return;
    hitEl = el;
    el.classList.remove('searchhit');
    void el.offsetWidth;          // 重新觸發動畫
    el.classList.add('searchhit');
  }

  // ── 段內關鍵字高亮 ────────────────────────────────────────
  // 著陸後只換目標段內的文字節點，包成 <mark class="kw">；原文／譯文文字不變。
  function getQueryParam() {
    var q = '';
    try { q = new URLSearchParams(location.search).get('q') || ''; }
    catch (e) {
      var mm = location.search.match(/[?&]q=([^&]*)/);
      if (mm) {
        try { q = decodeURIComponent(mm[1].replace(/\+/g, ' ')); } catch (err) { q = ''; }
      }
    }
    return q;
  }

  function escRe(s) {
    return String(s).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  var kwKey = '';
  function clearKw() {
    var marks = document.querySelectorAll('mark.kw');
    for (var i = 0; i < marks.length; i++) {
      var m = marks[i], p = m.parentNode;
      if (!p) continue;
      p.replaceChild(document.createTextNode(m.textContent || ''), m);
      p.normalize();
    }
    kwKey = '';
  }

  function markQuery(el) {
    if (!el) return;
    if (!el.classList.contains('pair') && !el.classList.contains('sec')) { clearKw(); return; }
    var terms = getQueryParam().split(/\s+/).filter(function (t) { return t.length > 0; });
    if (!terms.length) { clearKw(); return; }
    terms.sort(function (a, b) { return b.length - a.length; });
    var list = document.querySelectorAll('main .pair');
    var key = (el.id || ('pair-' + Array.prototype.indexOf.call(list, el))) + '|' + terms.join(' ');
    if (key === kwKey && el.querySelector('mark.kw')) return;
    clearKw();
    var re;
    try { re = new RegExp('(' + terms.map(escRe).join('|') + ')', 'gi'); }
    catch (e) { return; }
    var walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null);
    var nodes = [], n;
    while ((n = walker.nextNode())) {
      if (!n.nodeValue || !/\S/.test(n.nodeValue)) continue;
      var tag = n.parentNode ? n.parentNode.nodeName : '';
      if (/^(SCRIPT|STYLE|MARK|TEXTAREA)$/.test(tag)) continue;
      re.lastIndex = 0;
      if (re.test(n.nodeValue)) nodes.push(n);
    }
    nodes.forEach(function (node) {
      var text = node.nodeValue, frag = document.createDocumentFragment(), last = 0, m;
      re.lastIndex = 0;
      while ((m = re.exec(text)) !== null) {
        if (m.index > last) frag.appendChild(document.createTextNode(text.slice(last, m.index)));
        var mk = document.createElement('mark');
        mk.className = 'kw';
        mk.textContent = m[0];
        frag.appendChild(mk);
        last = m.index + m[0].length;
        if (m.index === re.lastIndex) re.lastIndex++;
      }
      if (!frag.childNodes.length) return;
      if (last < text.length) frag.appendChild(document.createTextNode(text.slice(last)));
      node.parentNode.replaceChild(frag, node);
    });
    kwKey = key;
  }

  function jumpToHash() {
    if (!location.hash) return;
    var id;
    try { id = decodeURIComponent(location.hash.slice(1)); }
    catch (e) { id = location.hash.slice(1); }
    var el = resolveAnchor(id);
    if (!el) return;
    markHit(el);
    markQuery(el);

    var seq = ++jumpSeq;
    userMoved = false;
    var tries = 0, last = null, stable = 0;

    (function settle() {
      if (userMoved || seq !== jumpSeq) return;
      var top = Math.max(0, Math.round(
        el.getBoundingClientRect().top + window.pageYOffset - topGap()));
      if (last !== null && Math.abs(top - last) <= 1) {
        if (++stable >= 2) {
          // 落地後重算「目前位置」；讓側欄高亮與畫面一致
          if (heads.length) { headTops = heads.map(function (h) {
            return h.getBoundingClientRect().top + window.pageYOffset;
          }); }
          syncCurrentByScroll();
          // 讓螢幕閱讀器知道到了哪一段（不捲動畫面）
          if (el.id && el.focus) {
            if (!el.hasAttribute('tabindex')) el.setAttribute('tabindex', '-1');
            try { el.focus({ preventScroll: true }); } catch (err) { el.focus(); }
          }
          return;
        }
      } else {
        stable = 0;
        last = top;
        window.scrollTo(0, top);
      }
      if (++tries < 12) setTimeout(settle, tries < 6 ? 50 : 120);
    })();
  }

  // 先立即定位一次：即使 nav.json 還沒回來（或載入失敗），pair 錨點也能到位
  jumpToHash();

  // ── 抽屜 ─────────────────────────────────────────────────
  function openDrawer() {
    if (!isMobile() || drawerOpen) return;
    drawerOpen = true;
    document.body.classList.add('nav-open');
    if (scrim) scrim.hidden = false;
    if (toggle) toggle.setAttribute('aria-expanded', 'true');
    if (nav) {
      nav.removeAttribute('inert');
      nav.removeAttribute('aria-hidden');
    }
    if (closeBtn) closeBtn.focus();
  }

  function closeDrawer(returnFocus) {
    if (!drawerOpen) return;
    drawerOpen = false;
    document.body.classList.remove('nav-open');
    if (scrim) scrim.hidden = true;
    if (toggle) toggle.setAttribute('aria-expanded', 'false');
    if (nav && isMobile()) {
      nav.setAttribute('inert', '');
      nav.setAttribute('aria-hidden', 'true');
    }
    if (returnFocus && toggle) toggle.focus();
  }

  function syncDrawerMode() {
    if (!isMobile()) {
      closeDrawer(false);
      if (nav) {
        nav.removeAttribute('inert');
        nav.removeAttribute('aria-hidden');
      }
      if (scrim) scrim.hidden = true;
    } else if (!drawerOpen && nav) {
      nav.setAttribute('inert', '');
      nav.setAttribute('aria-hidden', 'true');
    }
  }

  function trapFocus(e) {
    if (!drawerOpen || e.key !== 'Tab' || !nav) return;
    var items = [].slice.call(nav.querySelectorAll('a[href],button,input,summary,[tabindex]')).filter(function (el) {
      return !el.disabled && el.offsetParent !== null;
    });
    if (!items.length) return;
    var first = items[0], last = items[items.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault(); last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault(); first.focus();
    }
  }

  function globalKey(e) {
    if (e.key === 'Escape') {
      if (drawerOpen) { e.preventDefault(); closeDrawer(true); return; }
      if (filter && document.activeElement === filter) {
        e.preventDefault(); clearFilter(); filter.blur(); return;
      }
    }
    // 修飾鍵快捷鍵：焦點在輸入框裡也要生效
    if ((e.ctrlKey || e.metaKey) && !e.altKey && String(e.key || '').toLowerCase() === 'k') {
      e.preventDefault();
      if (siteSearch) { siteSearch.focus(); siteSearch.select(); return; }
      // 書頁上把側欄篩選字帶進全文搜尋（P1-12）
      var qv = filter && filter.value ? filter.value.trim() : '';
      location.href = root + 'search.html' + (qv ? '?q=' + encodeURIComponent(qv) : '');
      return;
    }
    if (e.target && /input|textarea|select/i.test(e.target.tagName)) return;
    if (e.key === '/' && !e.ctrlKey && !e.metaKey && !e.altKey) {
      e.preventDefault();
      if (siteSearch) { siteSearch.focus(); siteSearch.select(); return; }
      if (!filter) return;
      if (isMobile() && !drawerOpen) openDrawer();
      filter.focus();
    }
  }

  // ── 載入 ─────────────────────────────────────────────────
  function loadTree() {
    box.innerHTML = '<div class="navloading" role="status">目錄載入中…</div>';
    fetch(root + 'nav.json?v=' + version, { cache: 'no-cache' })
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(function (data) {
        DATA = data;
        curBook = bookOfPath() || readStr(BOOK_KEY);
        render();
        var restored = restoreScroll();
        spy();
        if (!restored) revealCurrent();
        jumpToHash();
      })
      .catch(function () {
        box.innerHTML = '<div class="navfail">目錄載入失敗。<button type="button" id="navretry">重試</button></div>';
        var b = document.getElementById('navretry');
        if (b) b.addEventListener('click', loadTree);
      });
  }

  // ── 閱讀工具列（P2-3 顯示切換、P2-4 雙欄、P1-6 複製連結）───────
  var READ_KEY = 'dsh-read-mode';
  var TWO_KEY = 'dsh-twocol';

  function syncReadButtons(bar) {
    var mode = 'both';
    if (document.documentElement.classList.contains('hide-t')) mode = 'o';
    else if (document.documentElement.classList.contains('hide-o')) mode = 't';
    [].slice.call(bar.querySelectorAll('button[data-read]')).forEach(function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-read') === mode ? 'true' : 'false');
    });
    var two = bar.querySelector('button[data-twocol-toggle]');
    if (two) two.setAttribute('aria-pressed',
      document.documentElement.classList.contains('twocol') ? 'true' : 'false');
  }

  function setReadMode(mode) {
    var h = document.documentElement;
    h.classList.remove('hide-o', 'hide-t');
    if (mode === 'o') h.classList.add('hide-t');        // 只原文 → 隱藏白話
    else if (mode === 't') h.classList.add('hide-o');   // 只白話 → 隱藏原文
    writeStr(READ_KEY, mode || 'both');
    // 版面高度變了，重算節位置與所在篇
    collectHeads();
    syncCurrentByScroll();
  }

  function setTwocol(on) {
    document.documentElement.classList.toggle('twocol', !!on);
    writeStr(TWO_KEY, on ? '1' : '0');
    collectHeads();
    syncCurrentByScroll();
  }

  function topVisibleAnchor() {
    var list = document.querySelectorAll('main .pair[id], main h2.sec[id]');
    var y = window.pageYOffset + topGap() + 8;
    var best = null;
    for (var i = 0; i < list.length; i++) {
      var top = list[i].getBoundingClientRect().top + window.pageYOffset;
      if (top <= y) best = list[i];
      else break;
    }
    return best || (list.length ? list[0] : null);
  }

  function copyText(s) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(s);
    }
    return new Promise(function (resolve, reject) {
      var ta = document.createElement('textarea');
      ta.value = s;
      ta.setAttribute('readonly', '');
      ta.style.position = 'fixed';
      ta.style.left = '-9999px';
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy') ? resolve() : reject(new Error('copy failed')); }
      catch (e) { reject(e); }
      document.body.removeChild(ta);
    });
  }

  function initReadTools() {
    var bar = document.querySelector('.readtools');
    if (!bar) return;
    syncReadButtons(bar);
    bar.addEventListener('click', function (e) {
      var btn = e.target.closest ? e.target.closest('button') : null;
      if (!btn) return;
      if (btn.hasAttribute('data-read')) {
        setReadMode(btn.getAttribute('data-read'));
        syncReadButtons(bar);
        return;
      }
      if (btn.hasAttribute('data-twocol-toggle')) {
        setTwocol(!document.documentElement.classList.contains('twocol'));
        syncReadButtons(bar);
        return;
      }
      if (btn.hasAttribute('data-copy-anchor')) {
        var el = topVisibleAnchor();
        var url = location.origin + location.pathname + (el && el.id ? '#' + el.id : '');
        var old = btn.textContent;
        copyText(url).then(function () {
          btn.textContent = '已複製';
          setTimeout(function () { btn.textContent = old; }, 1400);
        }).catch(function () {
          btn.textContent = '複製失敗';
          setTimeout(function () { btn.textContent = old; }, 1400);
        });
      }
    });
  }

  // skip link：把焦點真的移進 main（P1-7）
  var skip = document.querySelector('.skip-link');
  if (skip) {
    skip.addEventListener('click', function () {
      var m = document.getElementById('main');
      if (m) setTimeout(function () { m.focus({ preventScroll: true }); }, 0);
    });
  }

  // 初始化
  makeTools();
  initReadTools();
  loadTree();
  syncDrawerMode();

  if (toggle) toggle.addEventListener('click', function () {
    if (drawerOpen) closeDrawer(true); else openDrawer();
  });
  if (closeBtn) closeBtn.addEventListener('click', function () { closeDrawer(true); });
  if (scrim) scrim.addEventListener('click', function () { closeDrawer(true); });
  document.addEventListener('keydown', function (e) { trapFocus(e); globalKey(e); });

  if (isMobileQuery) {
    var onMode = function () { syncDrawerMode(); };
    if (isMobileQuery.addEventListener) isMobileQuery.addEventListener('change', onMode);
    else if (isMobileQuery.addListener) isMobileQuery.addListener(onMode);
  }

  // 同一頁內的錨點：交給瀏覽器預設行為前先攔下來，避免整頁重載
  box.addEventListener('click', function (e) {
    var a = e.target.closest ? e.target.closest('a') : null;
    if (!a) return;
    var u;
    try { u = new URL(a.href, location.href); } catch (err) { return; }
    if (u.pathname !== location.pathname || !u.hash) {
      if (isMobile()) closeDrawer(false);
      return;
    }
    e.preventDefault();
    if (history.pushState) history.pushState(null, '', u.hash);
    else location.hash = u.hash;
    jumpToHash();
    if (isMobile()) closeDrawer(false);
  });

  window.addEventListener('hashchange', function () { setTimeout(jumpToHash, 0); });
  window.addEventListener('load', function () { setTimeout(jumpToHash, 0); });

  // 回頂端
  var top = document.getElementById('toTop');
  if (!top) {
    top = document.createElement('button');
    top.id = 'toTop';
    top.type = 'button';
    top.setAttribute('aria-label', '回到頁面頂端');
    top.textContent = '↑ 回頂端';
    document.body.appendChild(top);
  }
  top.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });
  window.addEventListener('scroll', function () {
    top.classList.toggle('show', window.scrollY > 600);
  }, { passive: true });
})();
