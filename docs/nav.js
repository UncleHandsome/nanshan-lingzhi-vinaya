/* 側欄與全站導覽 v8：書 → 卷 → 篇 三層鑽取、跨書篩選、所在篇、抽屜、快捷鍵 */
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
      '<input id="navfilter" type="search" placeholder="搜尋書名、卷名、篇名" autocomplete="off" ' +
      'aria-label="搜尋目錄" aria-controls="navtree">' +
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
    if (!groups.length) html = '<p class="navempty">沒有符合「' + esc(filter.value.trim()) + '」的條目</p>';

    resultsEl.innerHTML = html;
    resultsEl.hidden = false;
    bodyEl.hidden = true;
    if (filterCount) {
      filterCount.textContent = total > 300 ? '300+' : (total ? total + ' 篇' : '無結果');
    }
  }

  // ── 所在篇高亮 ────────────────────────────────────────────
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
    activeLink = box.querySelector('a.cursec');

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

  function jumpToHash() {
    if (!location.hash) return;
    var id;
    try { id = decodeURIComponent(location.hash.slice(1)); }
    catch (e) { id = location.hash.slice(1); }
    var el = document.getElementById(id);
    if (!el) return;

    var seq = ++jumpSeq;
    userMoved = false;
    var tries = 0, last = null, stable = 0;

    (function settle() {
      if (userMoved || seq !== jumpSeq) return;
      var top = Math.max(0, Math.round(
        el.getBoundingClientRect().top + window.pageYOffset - topGap()));
      if (last !== null && Math.abs(top - last) <= 1) {
        if (++stable >= 2) return;
      } else {
        stable = 0;
        last = top;
        window.scrollTo(0, top);
      }
      if (++tries < 12) setTimeout(settle, tries < 6 ? 50 : 120);
    })();
  }

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

  // ── 載入 ─────────────────────────────────────────────────
  function loadTree() {
    box.innerHTML = '<div class="navloading">目錄載入中…</div>';
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
