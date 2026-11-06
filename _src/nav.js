/* 側欄樹：由 nav.json 產生，記住展開狀態、標示所在卷 */
(function () {
  var box = document.getElementById('navtree');
  if (!box) return;
  var root = box.getAttribute('data-root') || '';
  var path = decodeURIComponent(location.pathname);
  var KEY = 'dsh-nav-open';
  var saved = {};
  try { saved = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { saved = {}; }

  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
  function keyOf(t) { return t.replace(/\s+/g, ''); }
  function isOpen(t) {
    var k = keyOf(t);
    return (k in saved) ? saved[k] : false;
  }
  function setOpen(t, v) {
    saved[keyOf(t)] = v;
    try { localStorage.setItem(KEY, JSON.stringify(saved)); } catch (e) {}
  }

  fetch(root + 'nav.json?v=3').then(function (r) { return r.json(); }).then(function (data) {
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
            html += '<li><a href="' + root + b.out + '/' + v.v + '.html#' + s[0] + '">' + esc(s[1]) + '</a></li>';
          });
        }
        html += '</ul></details>';
      });
      html += '</details>';
    });
    box.innerHTML = html;
    box.querySelectorAll('details').forEach(function (d) {
      d.addEventListener('toggle', function () {
        if (d.classList.contains('tk')) setOpen(d.querySelector('summary').textContent, d.open);
        else {
          var bk = d.closest('details.tk');
          if (bk) setOpen(bk.querySelector('summary').textContent + '/' + d.querySelector('summary').textContent, d.open);
        }
      });
    });

  // 捲動時高亮所在篇目
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

  // 目錄點擊後：等 nav 重建完再回到錨點，避免「重刷後跑掉」
  function jump() {
    if (!location.hash) return;
    var el = document.getElementById(location.hash.slice(1));
    if (el) el.scrollIntoView({ block: 'start', behavior: 'auto' });
  }
  function restoreHash() {
    [0, 120, 320, 700].forEach(function (ms) { setTimeout(jump, ms); });
  }
  spy();
  restoreHash();
  window.addEventListener('load', restoreHash);
  window.addEventListener('hashchange', function () { setTimeout(jump, 0); setTimeout(jump, 200); });
  }).catch(function () {
    box.innerHTML = '<a href="' + root + 'index.html">目錄</a>';
  });
})();
