/* 側欄樹 v6：nav.json 產生、展開記憶、所在卷標示、篩選、快捷鍵 */
(function () {
  var box = document.getElementById('navtree');
  if (!box) return;
  var root = box.getAttribute('data-root') || '';
  var path = decodeURIComponent(location.pathname);
  var KEY = 'dsh-nav-open';
  var SKEY = 'dsh-nav-scroll';
  var saved = {};
  try { saved = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { saved = {}; }

  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
  function keyOf(t) { return t.replace(/\s+/g, ''); }
  function isOpen(t) { var k = keyOf(t); return (k in saved) ? saved[k] : false; }
  function setOpen(t, v) { saved[keyOf(t)] = v; try { localStorage.setItem(KEY, JSON.stringify(saved)); } catch (e) {} }

  // 工具列（篩選 + 展開/收合）
  var tools = document.createElement('div');
  tools.className = 'navtools';
  tools.innerHTML = '<input id="navfilter" type="search" placeholder="篩選篇目（按 / 聚焦）" autocomplete="off">'
    + '<div class="navbtns"><button type="button" id="navopen">展開</button><button type="button" id="navclose">收合</button></div>';
  box.parentNode.insertBefore(tools, box);

  fetch(root + 'nav.json?v=6').then(function (r) { return r.json(); }).then(function (data) {
    var here = path;
    var html = '';
    (data.books || []).forEach(function (b) {
      var inBook = here.indexOf('/' + b.out + '/') >= 0;
      var open = inBook || isOpen(b.title);
      html += '<details class="tk"' + (open ? ' open' : '') + ' data-key="' + esc(keyOf(b.title)) + '">'
            + '<summary>' + esc(b.title) + '</summary>';
      (b.vols || []).forEach(function (v) {
        var cur = here.indexOf('/' + b.out + '/' + v.v + '.html') >= 0;
        var vopen = cur || isOpen(b.title + '/' + v.v);
        html += '<details class="vk"' + (vopen ? ' open' : '') + ' data-key="' + esc(keyOf(b.title + '/' + v.v)) + '">'
              + '<summary' + (cur ? ' class="cur"' : '') + '>' + esc(v.v) + '</summary><ul>';
        var secs = v.secs || [];
        if (!secs.length) {
          html += '<li><a href="' + root + b.out + '/' + v.v + '.html">（全卷）</a></li>';
        } else {
          secs.forEach(function (s) {
            html += '<li><a data-t="' + esc(s[1]) + '" href="' + root + b.out + '/' + v.v + '.html#' + s[0] + '">' + esc(s[1]) + '</a></li>';
          });
        }
        html += '</ul></details>';
      });
      html += '</details>';
    });
    box.innerHTML = html;
    var all = box.querySelectorAll('details');
    all.forEach(function (d) {
      d.addEventListener('toggle', function () {
        if (d.classList.contains('tk')) setOpen(d.querySelector('summary').textContent, d.open);
        else {
          var bk = d.closest('details.tk');
          if (bk) setOpen(bk.querySelector('summary').textContent + '/' + d.querySelector('summary').textContent, d.open);
        }
      });
    });
    // 還原側欄捲動位置
    try { var sc = parseInt(localStorage.getItem(SKEY) || '0', 10); if (sc) box.parentNode.scrollTop = sc; } catch (e) {}
    box.parentNode.addEventListener('scroll', function () {
      try { localStorage.setItem(SKEY, String(box.parentNode.scrollTop)); } catch (e) {}
    }, { passive: true });
    // 所在卷高亮
    var curSum = box.querySelector('summary.cur');
    if (curSum) { var t = curSum.closest('details.tk'); if (t) t.open = true; curSum.scrollIntoView({ block: 'nearest' }); }
    spy();
  }).catch(function () {
    box.innerHTML = '<a href="' + root + 'index.html">目錄</a>';
  });

  // 篩選
  var filter = document.getElementById('navfilter');
  function applyFilter() {
    var q = (filter.value || '').trim();
    box.querySelectorAll('li').forEach(function (li) {
      var a = li.querySelector('a');
      var hit = !q || (a && (a.getAttribute('data-t') || '').indexOf(q) >= 0);
      li.style.display = hit ? '' : 'none';
    });
    if (q) {
      box.querySelectorAll('details').forEach(function (d) { if (d.querySelector('li:not([style*="none"])')) d.open = true; });
    }
  }
  if (filter) {
    filter.addEventListener('input', applyFilter);
    filter.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { filter.value = ''; applyFilter(); filter.blur(); }
      if (e.key === 'Enter') {
        var a = box.querySelector('li:not([style*="none"]) a');
        if (a) { a.click(); filter.blur(); }
      }
    });
  }
  var bopen = document.getElementById('navopen'), bclose = document.getElementById('navclose');
  if (bopen) bopen.addEventListener('click', function () {
    box.querySelectorAll('details').forEach(function (d) { d.open = true; });
  });
  if (bclose) bclose.addEventListener('click', function () {
    box.querySelectorAll('details').forEach(function (d) { d.open = false; });
  });

  // 全域快捷鍵：/ 篩選、Ctrl/Cmd+K 搜尋
  document.addEventListener('keydown', function (e) {
    if (e.target && /input|textarea|select/i.test(e.target.tagName)) return;
    if (e.key === '/' && filter) { e.preventDefault(); filter.focus(); }
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      location.href = root + 'search.html';
    }
  });

  function spy() {
    var heads = [].slice.call(document.querySelectorAll('h2.sec'));
    if (!heads.length || !('IntersectionObserver' in window)) return;
    var links = {};
    [].slice.call(box.querySelectorAll('a[href*="#p"]')).forEach(function (a) {
      var id = a.getAttribute('href').split('#')[1];
      if (id) links[id] = a;
    });
    var cur = null;
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        var a = links[e.target.id];
        if (!a) return;
        if (cur) cur.classList.remove('cursec');
        cur = a;
        a.classList.add('cursec');
        var d = a.closest('details.vk'); if (d && !d.open) d.open = true;
        var t = a.closest('details.tk'); if (t && !t.open) t.open = true;
      });
    }, { rootMargin: '-8% 0px -82% 0px' });
    heads.forEach(function (h) { io.observe(h); });
  }

  function jump() {
    if (!location.hash) return;
    var el = document.getElementById(location.hash.slice(1));
    if (!el) return;
    var de = document.documentElement;
    var old = de.style.scrollBehavior;
    de.style.scrollBehavior = 'auto';
    el.scrollIntoView({ block: 'start', behavior: 'instant' });
    de.style.scrollBehavior = old;
  }
  function restoreHash() { [0, 120, 320, 700].forEach(function (ms) { setTimeout(jump, ms); }); }

  box.addEventListener('click', function (e) {
    var a = e.target.closest ? e.target.closest('a') : null;
    if (!a) return;
    var u;
    try { u = new URL(a.href, location.href); } catch (err) { return; }
    if (u.pathname !== location.pathname || !u.hash) return;
    e.preventDefault();
    var id = u.hash.slice(1);
    var el = document.getElementById(id);
    if (!el) return;
    if (history.pushState) history.pushState(null, '', u.hash);
    else location.hash = u.hash;
    var de = document.documentElement, old = de.style.scrollBehavior;
    de.style.scrollBehavior = 'auto';
    el.scrollIntoView({ block: 'start', behavior: 'instant' });
    de.style.scrollBehavior = old;
  });
  restoreHash();
  window.addEventListener('load', restoreHash);
  window.addEventListener('hashchange', function () { setTimeout(jump, 0); setTimeout(jump, 200); });

  // 回到頂端
  var top = document.createElement('button');
  top.id = 'toTop'; top.type = 'button'; top.textContent = '↑ 回頂端';
  top.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });
  document.body.appendChild(top);
  window.addEventListener('scroll', function () {
    top.classList.toggle('show', window.scrollY > 600);
  }, { passive: true });
})();
