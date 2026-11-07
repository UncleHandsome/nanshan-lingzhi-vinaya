/* 側欄與全站導覽 v7：三層目錄、篩選、所在卷、抽屜、快捷鍵 */
(function () {
  'use strict';

  var box = document.getElementById('navtree');
  if (!box) return;

  var nav = document.getElementById('sidebar') || box.closest('nav');
  var root = box.getAttribute('data-root') || '';
  var version = box.getAttribute('data-nav-version') || '11';
  var path = safePath();
  var isMobileQuery = window.matchMedia ? window.matchMedia('(max-width: 1100px)') : null;
  var OPEN_KEY = 'dsh-nav-open-v2';
  var SCROLL_KEY = 'dsh-nav-scroll-v2:' + path;
  var saved = readJSON(OPEN_KEY, {});
  var filter = null;
  var filterCount = null;
  var filtering = false;
  var preFilter = null;
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

  function readJSON(key, fallback) {
    try {
      var v = JSON.parse(localStorage.getItem(key) || 'null');
      return v && typeof v === 'object' ? v : fallback;
    } catch (e) { return fallback; }
  }

  function writeJSON(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) {}
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

  function setUserOpen(key, value) {
    saved[key] = !!value;
    writeJSON(OPEN_KEY, saved);
  }

  function savedOpen(key) {
    return !!saved[key];
  }

  function makeTools() {
    var tools = document.createElement('div');
    tools.className = 'navtools';
    tools.innerHTML =
      '<div class="navfilterwrap">' +
      '<input id="navfilter" type="search" placeholder="篩選書名、卷名、篇名（按 / 聚焦）" autocomplete="off" aria-label="篩選目錄">' +
      '<span id="navfiltercount" class="navfiltercount" aria-live="polite"></span>' +
      '</div>' +
      '<div class="navbtns"><button type="button" id="navopen">展開</button>' +
      '<button type="button" id="navcloseall">收合</button></div>';
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
        var a = firstVisibleLink();
        if (a) { a.click(); filter.blur(); }
      }
    });

    document.getElementById('navopen').addEventListener('click', function () {
      clearFilter();
      box.querySelectorAll('details').forEach(function (d) { d.open = true; });
    });
    document.getElementById('navcloseall').addEventListener('click', function () {
      clearFilter();
      box.querySelectorAll('details').forEach(function (d) { d.open = false; });
    });
  }

  function firstVisibleLink() {
    var links = box.querySelectorAll('li:not([hidden]) a[href]');
    for (var i = 0; i < links.length; i++) {
      if (links[i].offsetParent !== null) return links[i];
    }
    return null;
  }

  function clearFilter() {
    if (!filter) return;
    filter.value = '';
    applyFilter();
  }

  function snapshotOpen() {
    if (preFilter) return;
    preFilter = {};
    box.querySelectorAll('details').forEach(function (d) {
      preFilter[d.getAttribute('data-key') || ''] = d.open;
    });
  }

  function restoreOpen() {
    if (!preFilter) return;
    filtering = true;
    box.querySelectorAll('details').forEach(function (d) {
      var k = d.getAttribute('data-key') || '';
      d.hidden = false;
      if (k in preFilter) d.open = preFilter[k];
    });
    filtering = false;
    preFilter = null;
    if (filterCount) filterCount.textContent = '';
  }

  function applyFilter() {
    if (!filter) return;
    var q = norm(filter.value.trim());
    if (!q) { restoreOpen(); return; }
    snapshotOpen();
    filtering = true;
    var total = 0;
    box.querySelectorAll('details.tk').forEach(function (book) {
      var bookHit = norm(book.getAttribute('data-title')).indexOf(q) >= 0;
      var anyVol = false;
      book.querySelectorAll('details.vk').forEach(function (vol) {
        var volHit = norm(vol.getAttribute('data-title')).indexOf(q) >= 0;
        var anyLi = false;
        vol.querySelectorAll('li').forEach(function (li) {
          var hit = bookHit || volHit || norm(li.getAttribute('data-t')).indexOf(q) >= 0;
          li.hidden = !hit;
          if (hit) { anyLi = true; total++; }
        });
        var show = bookHit || volHit || anyLi;
        vol.hidden = !show;
        vol.open = show;
        if (show) anyVol = true;
      });
      var showBook = bookHit || anyVol;
      book.hidden = !showBook;
      book.open = showBook;
    });
    filtering = false;
    if (filterCount) filterCount.textContent = total ? total + ' 篇' : '無結果';
  }

  function buildTree(data) {
    var html = '';
    (data.books || []).forEach(function (b) {
      var inBook = path.indexOf('/' + b.out + '/') >= 0;
      var open = inBook || savedOpen(b.out);
      html += '<details class="tk"' + (open ? ' open' : '') +
        ' data-key="' + esc(b.out) + '" data-title="' + esc(b.title) + '">' +
        '<summary>' + esc(b.title) + '</summary>';
      (b.vols || []).forEach(function (v) {
        var cur = path.indexOf('/' + b.out + '/' + v.v + '.html') >= 0;
        var vopen = cur || savedOpen(b.out + '/' + v.v);
        var vkey = b.out + '/' + v.v;
        html += '<details class="vk"' + (vopen ? ' open' : '') +
          ' data-key="' + esc(vkey) + '" data-title="' + esc(v.v) + '">' +
          '<summary' + (cur ? ' class="cur" aria-current="page"' : '') + '>' + esc(v.v) + '</summary><ul>';
        var secs = v.secs || [];
        if (!secs.length) {
          html += '<li data-t="全卷"><a href="' + root + b.out + '/' + v.v + '.html">（全卷）</a></li>';
        } else {
          secs.forEach(function (s) {
            var href = root + b.out + '/' + v.v + '.html#' + s[0];
            html += '<li data-t="' + esc(s[1]) + '"><a data-t="' + esc(s[1]) + '" href="' + href + '">' + esc(s[1]) + '</a></li>';
          });
        }
        html += '</ul></details>';
      });
      html += '</details>';
    });
    box.innerHTML = html;
    bindDetails();
    var restored = restoreScroll();
    focusCurrent(restored);
    spy();
    jumpToHash();
  }

  function bindDetails() {
    box.querySelectorAll('details').forEach(function (d) {
      d.addEventListener('toggle', function () {
        if (filtering || preFilter) return;
        var k = d.getAttribute('data-key') || '';
        if (k) setUserOpen(k, d.open);
      });
    });
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

  // keepScroll：本次載入已還原使用者上次的位置，就不要把它拉回「所在卷」
  function focusCurrent(keepScroll) {
    var cur = box.querySelector('summary.cur');
    if (!cur || !nav) return;
    var book = cur.closest('details.tk');
    if (book) book.open = true;
    if (keepScroll) return;
    var top = cur.getBoundingClientRect().top - nav.getBoundingClientRect().top + nav.scrollTop - 24;
    nav.scrollTop = Math.max(0, top);
  }

  // 行動版頂欄是 fixed，錨點捲動要讓開它的高度
  function topGap() {
    var bar = document.querySelector('.mobilebar');
    if (!bar) return 14;
    var cs = window.getComputedStyle(bar);
    if (cs.display === 'none' || cs.position !== 'fixed') return 14;
    return bar.getBoundingClientRect().height + 12;
  }

  function loadTree() {
    box.innerHTML = '<div class="navloading">目錄載入中…</div>';
    fetch(root + 'nav.json?v=' + version, { cache: 'no-cache' })
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(buildTree)
      .catch(function () {
        box.innerHTML = '<div class="navfail">目錄載入失敗。<button type="button" id="navretry">重試</button></div>';
      });
  }

  function spy() {
    var heads = [].slice.call(document.querySelectorAll('main h2.sec'));
    if (!heads.length) return;
    var links = {};
    [].slice.call(box.querySelectorAll('a[href*="#p"]')).forEach(function (a) {
      var u;
      try { u = new URL(a.href, location.href); } catch (e) { return; }
      if (u.pathname !== location.pathname) return;
      var id = u.hash.slice(1);
      if (id) links[id] = a;
    });
    if (!Object.keys(links).length) return;

    function setCurrent(a) {
      if (activeLink === a) return;
      if (activeLink) {
        activeLink.classList.remove('cursec');
        activeLink.removeAttribute('aria-current');
      }
      activeLink = a || null;
      if (activeLink) {
        activeLink.classList.add('cursec');
        activeLink.setAttribute('aria-current', 'location');
      }
    }

    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          var a = links[e.target.id];
          if (a) setCurrent(a);
        });
      }, { rootMargin: '-8% 0px -82% 0px' });
      heads.forEach(function (h) { io.observe(h); });
    } else {
      var onScroll = function () {
        var current = null;
        heads.forEach(function (h) {
          if (h.getBoundingClientRect().top <= 100) current = links[h.id] || current;
        });
        setCurrent(current);
      };
      window.addEventListener('scroll', onScroll, { passive: true });
      onScroll();
    }
  }

  function jumpToHash() {
    if (!location.hash) return;
    var id;
    try { id = decodeURIComponent(location.hash.slice(1)); }
    catch (e) { id = location.hash.slice(1); }
    var el = document.getElementById(id);
    if (!el) return;
    var top = el.getBoundingClientRect().top + window.pageYOffset - topGap();
    window.scrollTo(0, Math.max(0, top));
  }

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
      // 只在焦點確實落在側欄篩選框時才清它，避免在站內搜尋框按 Esc 誤清目錄篩選
      if (filter && document.activeElement === filter) {
        e.preventDefault(); clearFilter(); filter.blur(); return;
      }
    }
    // 修飾鍵快捷鍵：焦點在輸入框裡也要生效，否則邊篩選邊按 Ctrl+K 會沒反應
    if ((e.ctrlKey || e.metaKey) && !e.altKey && String(e.key || '').toLowerCase() === 'k') {
      e.preventDefault();
      if (siteSearch) { siteSearch.focus(); siteSearch.select(); }
      else location.href = root + 'search.html';
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

  // 初始化
  makeTools();
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

  box.addEventListener('click', function (e) {
    var retry = e.target.closest ? e.target.closest('#navretry') : null;
    if (retry) { loadTree(); return; }
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
