/* 全站導覽 v12（一篇一頁）：全站頂部列、書 → 卷 → 篇三層鑽取、所在篇（scroll 推導）、
   閱讀模式（原文／白話／雙欄）、複製本段連結、桌面預設展開側欄、
   收合後左緣 hover／focus 露出、窄螢幕自動抽屜。
   v62：nav.json 的 secs = [anchor, label, 篇頁 stem]；側欄點篇直接進篇頁，
   「全卷」進卷目錄頁，當前篇用 aria-current="page" 高亮。 */
(function () {
  'use strict';

  var box = document.getElementById('navtree');
  if (!box) return;

  var nav = document.getElementById('sidebar') || box.closest('nav');
  var root = box.getAttribute('data-root') || '';
  var version = box.getAttribute('data-nav-version') || '12';
  var path = safePath();
  var curStem = pageStem();
  var isMobileQuery = window.matchMedia ? window.matchMedia('(max-width: 1100px)') : null;
  var BOOK_KEY = 'dsh-nav-book-v3';
  var SCROLL_KEY = 'dsh-nav-scroll-v3:' + path;
  var SIDE_KEY = 'dsh-nav-side-v2';
  var DATA = null;
  var curBook = null;
  var openVol = null;
  var bodyEl = null;
  var activeLink = null;
  var drawerOpen = false;
  var pinned = true;
  var peeking = false;
  var peekTimer = null;
  var toggle = document.getElementById('navtoggle');
  var closeBtn = document.getElementById('navclose');
  var scrim = document.getElementById('navscrim');
  var edge = document.getElementById('edgepeek');

  function safePath() {
    try { return decodeURIComponent(location.pathname); }
    catch (e) { return location.pathname; }
  }

  // 目前頁面 stem：卷目錄頁是「卷上」，篇頁是「卷上__p3」。
  function pageStem() {
    var m = /\/([^\/]+)\.html$/.exec(safePath());
    return m ? m[1] : '';
  }

  // 側欄／首頁樹的篇連結：新版 nav 的 sec[2] 是篇頁 stem；
  // 舊格式（只有兩欄）才退回卷頁 + 錨點，方便尚未重建的頁面。
  function secHref(bookOut, volName, sec) {
    if (sec && sec[2]) return root + bookOut + '/' + sec[2] + '.html';
    return root + bookOut + '/' + volName + '.html#' + (sec ? sec[0] : '');
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

  function isMobile() {
    return !!(isMobileQuery && isMobileQuery.matches);
  }

  // 全域搜尋：搜尋頁優先用主輸入框，其餘頁面用頂部列（≥1200px 才可見）。
  function visibleSearchBox() {
    var q = document.getElementById('q');
    if (q && q.offsetParent !== null) return q;
    var tb = document.getElementById('tbq');
    if (tb && tb.offsetParent !== null) return tb;
    return null;
  }

  function focusOrGoSearch() {
    var box = visibleSearchBox();
    if (box) { box.focus(); box.select(); return; }
    location.href = root + 'search.html';
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

  // 首頁與非書頁沒有「目前卷」：側欄只列書目，不顯示空的卷／篇 TOC。
  // 首頁／搜尋頁側欄：書 → 卷 → 篇 三層樹。
  // 點書名、卷名都只展開，不跳頁；點到最後一層（篇）才進入內文。
  // 篇名拆成「篇號 + 名稱」；合編的「標宗顯德篇」去掉尾字「篇」。
  function secParts(label) {
    var m = /^第\s*(\d+)\s*篇[\u3000\s]*(.*)$/.exec(label || '');
    if (m) return {num: m[1], name: m[2] || label};
    m = /^(.+?)篇$/.exec(label || '');
    if (m) return {num: '', name: m[1]};
    return {num: '', name: label || ''};
  }

  function renderHome() {
    var HOME_ORDER = {xingshichao: 0, zhichi: 1, hebian: 2, jieshu: 3, yeshu: 4, nicao: 5, yichao: 6};
    var books = (DATA.books || []).slice().sort(function (a, b) {
      return (HOME_ORDER[a.out] == null ? 99 : HOME_ORDER[a.out]) -
             (HOME_ORDER[b.out] == null ? 99 : HOME_ORDER[b.out]);
    });
    var html = '<p class="navgrouplabel">書目</p><div class="navhometree">';
    books.forEach(function (b) {
      var vols = b.vols || [];
      if (!vols.length) return;
      html += '<details class="navbookhome" data-book="' + esc(b.out) + '">' +
        '<summary><span class="bk">' + esc(b.title) + '</span>' +
        '<span class="bcount">' + vols.length + ' 卷</span></summary>' +
        '<ul class="vols">';
      vols.forEach(function (v) {
        var secs = v.secs || [];
        if (!secs.length) {
          html += '<li class="volitem"><a class="navvolwhole" href="' + root + b.out +
            '/' + v.v + '.html">' + esc(v.v) + '</a></li>';
          return;
        }
        html += '<li class="volitem"><details class="navvol"><summary>' +
          '<span class="vname">' + esc(v.v) + '</span>' +
          '<span class="vcount">' + secs.length + ' 篇</span></summary>' +
          '<ul class="secs">';
        secs.forEach(function (s) {
          var p = secParts(s[1]);
          html += '<li><a href="' + secHref(b.out, v.v, s) +
            '" title="' + esc(s[1]) + '">' +
            (p.num ? '<span class="secnum">' + esc(p.num) + '</span>' : '<span class="secdots">·</span>') +
            '<span class="secname">' + esc(p.name) + '</span></a></li>';
        });
        html += '</ul></details></li>';
      });
      html += '</ul></details>';
    });
    html += '</div>';

    bodyEl = document.createElement('div');
    bodyEl.className = 'navbody';
    bodyEl.innerHTML = html;
    box.innerHTML = '';
    box.appendChild(bodyEl);
    bindHomeTree();
  }

  // 首頁樹：同時只展開一本書（避免側欄過長）；卷可多個展開。
  function bindHomeTree() {
    if (!bodyEl) return;
    bodyEl.querySelectorAll('.navbookhome').forEach(function (d) {
      d.addEventListener('toggle', function () {
        if (!d.open) return;
        bodyEl.querySelectorAll('.navbookhome').forEach(function (o) {
          if (o !== d) o.open = false;
        });
      });
    });
  }

  function render() {
    // 首頁與搜尋／附錄／未譯等「不屬於任何書」的頁面：側欄列全部書目 → 卷。
    if (!bookOfPath()) { renderHome(); return; }
    var b = bookByOut(curBook) || (DATA.books || [])[0];
    if (!b) return;
    curBook = b.out;
    writeStr(BOOK_KEY, b.out);

    var html = '<div class="navvols">';
    (b.vols || []).forEach(function (v) {
      var isCurVolPage = curStem === v.v;
      var curSecInVol = false;
      (v.secs || []).forEach(function (s) {
        if (s[2] && s[2] === curStem) curSecInVol = true;
      });
      var open = isCurVolPage || curSecInVol || openVol === v.v;
      var n = (v.secs || []).length;
      html += '<details class="vol' + (isCurVolPage ? ' curpage' : '') + '"' +
        (open ? ' open' : '') + ' data-v="' + esc(v.v) + '">' +
        '<summary><span class="vname">' + esc(v.v) + '</span>' +
        '<span class="vcount">' + (n ? n + ' 篇' : '全卷') + '</span></summary><ul>' +
        '<li class="wholevol"><a href="' + root + b.out + '/' + v.v + '.html">全卷（卷目錄）</a></li>';
      (v.secs || []).forEach(function (s) {
        var here = !!(s[2] && s[2] === curStem) ||
          (!s[2] && isCurVolPage && location.hash === '#' + s[0]);
        html += '<li><a href="' + secHref(b.out, v.v, s) +
          '" title="' + esc(s[1]) + '"' +
          (here ? ' class="cursec" aria-current="page"' : '') + '>' + esc(s[1]) + '</a></li>';
      });
      html += '</ul></details>';
    });
    html += '</div>';

    bodyEl = document.createElement('div');
    bodyEl.className = 'navbody';
    bodyEl.innerHTML = html;

    box.innerHTML = '';
    box.appendChild(bodyEl);

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
    // 一篇一頁後篇連結不再帶 #pN；保留舊格式頁面的同頁錨點對應。
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
    // 篇頁只有一節、側欄連結也不帶錨點：保留 render() 靜態標好的 aria-current
    if (!cur) return;
    if (setCurrent(cur)) revealLink(cur);
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
    // 頂部列高度（單列；內容真正的上緣）
    var h = 0;
    var bar = document.querySelector('.topbar');
    if (bar) {
      var cs = window.getComputedStyle(bar);
      if (cs.display !== 'none') h = bar.getBoundingClientRect().height;
    }
    return h > 0 ? h + 12 : 14;
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
      if (++tries < 24) setTimeout(settle, tries < 6 ? 50 : 150);
    })();
  }

  // 先立即定位一次：即使 nav.json 還沒回來（或載入失敗），pair 錨點也能到位
  jumpToHash();

  // ── 側欄狀態：桌面 pinned／peek、窄螢幕 drawer ──────────────
  function navVisible() {
    return isMobile() ? drawerOpen : (pinned || peeking);
  }

  function syncNav() {
    var body = document.body;
    var mob = isMobile();
    body.classList.toggle('nav-drawer-open', mob && drawerOpen);
    body.classList.toggle('nav-collapsed', !mob && !pinned && !peeking);
    body.classList.toggle('nav-peek', !mob && peeking);
    var hidden = mob ? !drawerOpen : (!pinned && !peeking);
    if (nav) {
      if (hidden) {
        nav.setAttribute('inert', '');
        nav.setAttribute('aria-hidden', 'true');
      } else {
        nav.removeAttribute('inert');
        nav.removeAttribute('aria-hidden');
      }
    }
    if (scrim) scrim.hidden = !(mob && drawerOpen);
    if (toggle) {
      var vis = navVisible();
      toggle.setAttribute('aria-expanded', vis ? 'true' : 'false');
      toggle.setAttribute('aria-label', vis ? '收合目錄' : '展開目錄');
      toggle.title = (vis ? '收合目錄' : '展開目錄') + '（[ 或 Alt+M）';
    }
  }

  function setPinned(on, save) {
    pinned = !!on;
    if (pinned) peeking = false;
    clearTimeout(peekTimer);
    syncNav();
    if (save) writeStr(SIDE_KEY, pinned ? 'open' : 'collapsed');
  }

  function openPeek() {
    if (isMobile() || pinned) return;
    clearTimeout(peekTimer);
    if (!peeking) {
      peeking = true;
      syncNav();
    }
  }

  function closePeek(delay) {
    if (!peeking) return;
    clearTimeout(peekTimer);
    peekTimer = setTimeout(function () {
      if (nav && nav.contains(document.activeElement)) return;
      peeking = false;
      syncNav();
    }, typeof delay === 'number' ? delay : 160);
  }

  function openDrawer() {
    if (!isMobile() || drawerOpen) return;
    drawerOpen = true;
    syncNav();
    if (closeBtn) closeBtn.focus();
  }

  function closeDrawer(returnFocus) {
    if (!isMobile() || !drawerOpen) return;
    drawerOpen = false;
    syncNav();
    if (returnFocus && toggle) toggle.focus();
  }

  function toggleNav() {
    if (isMobile()) {
      if (drawerOpen) closeDrawer(true); else openDrawer();
    } else {
      setPinned(!pinned, true);
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
      if (peeking) { e.preventDefault(); peeking = false; syncNav(); return; }
      if (drawerOpen) { e.preventDefault(); closeDrawer(true); return; }
    }
    // 修飾鍵快捷鍵：焦點在輸入框裡也要生效
    if ((e.ctrlKey || e.metaKey) && !e.altKey && String(e.key || '').toLowerCase() === 'k') {
      e.preventDefault();
      focusOrGoSearch();
      return;
    }
    if (e.target && /input|textarea|select/i.test(e.target.tagName)) return;
    // 目錄開合：Alt+M 或 [（不搶輸入框；不用先找按鈕）
    if ((e.altKey && !e.ctrlKey && !e.metaKey && String(e.key || '').toLowerCase() === 'm') ||
        (e.key === '[' && !e.ctrlKey && !e.metaKey && !e.altKey)) {
      e.preventDefault();
      toggleNav();
      return;
    }
    if (e.key === '/' && !e.ctrlKey && !e.metaKey && !e.altKey) {
      e.preventDefault();
      focusOrGoSearch();
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

  // ── 閱讀工具列（原文／白話各自開關、雙欄、複製連結）───────
  var SHOW_O_KEY = 'dsh-show-o';
  var SHOW_T_KEY = 'dsh-show-t';
  var TWO_KEY = 'dsh-twocol';

  function showState() {
    var h = document.documentElement;
    return {o: !h.classList.contains('hide-o'), t: !h.classList.contains('hide-t')};
  }

  function syncReadButtons(bar) {
    var st = showState();
    [].slice.call(bar.querySelectorAll('button[data-show]')).forEach(function (b) {
      var isO = b.getAttribute('data-show') === 'o';
      var on = isO ? st.o : st.t;
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      b.title = (on ? '隱藏' : '顯示') + (isO ? '原文' : '白話');
    });
    var two = bar.querySelector('button[data-twocol-toggle]');
    if (two) {
      var wide = !window.matchMedia || window.matchMedia('(min-width: 1200px)').matches;
      two.disabled = !wide;
      two.title = wide ? '原文與白話左右並排' : '視窗需至少 1200px 才能並排';
      two.setAttribute('aria-pressed',
        document.documentElement.classList.contains('twocol') ? 'true' : 'false');
    }
  }

  function setShow(side, on) {
    var h = document.documentElement;
    h.classList.toggle(side === 'o' ? 'hide-o' : 'hide-t', !on);
    writeStr(side === 'o' ? SHOW_O_KEY : SHOW_T_KEY, on ? '1' : '0');
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
    var bar = document.querySelector('.tb-readtools') || document.querySelector('.readtools');
    if (!bar) return;
    syncReadButtons(bar);
    bar.addEventListener('click', function (e) {
      var btn = e.target.closest ? e.target.closest('button') : null;
      if (!btn) return;
      if (btn.hasAttribute('data-show')) {
        var side = btn.getAttribute('data-show');
        var st = showState();
        setShow(side, side === 'o' ? !st.o : !st.t);
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

  // ── 段別隱藏（記文／註文／律文／序文／疏文／鈔文）────────
  function initLabelFilters() {
    var btns = [].slice.call(document.querySelectorAll('button[data-hide-label]'));
    if (!btns.length) return;
    var KEY = 'dsh-hide-labels-v1';
    var saved = {};
    try { saved = JSON.parse(readStr(KEY) || '{}') || {}; } catch (e) { saved = {}; }
    btns.forEach(function (btn) {
      var cls = btn.getAttribute('data-hide-label');
      var has = !!document.querySelector('.pair.' + cls);
      btn.hidden = !has;
      if (!has) return;
      function set(hidden, save) {
        document.documentElement.classList.toggle('hide-' + cls, hidden);
        btn.setAttribute('aria-pressed', hidden ? 'false' : 'true');
        btn.title = (hidden ? '顯示' : '隱藏') + btn.textContent.trim();
        saved[cls] = !!hidden;
        if (save) writeStr(KEY, JSON.stringify(saved));
      }
      set(!!saved[cls], false);
      btn.addEventListener('click', function () {
        set(!document.documentElement.classList.contains('hide-' + cls), true);
        collectHeads();
        syncCurrentByScroll();
      });
    });
    var wrap = document.querySelector('.tb-labelseg');
    if (wrap && !btns.some(function (b) { return !b.hidden; })) wrap.hidden = true;
  }

  var bookPick = document.getElementById('tb-bookpick');
  if (bookPick) bookPick.addEventListener('change', function () {
    if (bookPick.value) location.href = bookPick.value;
  });

  // skip link：把焦點真的移進 main（P1-7）
  var skip = document.querySelector('.skip-link');
  if (skip) {
    skip.addEventListener('click', function () {
      var m = document.getElementById('main');
      if (m) setTimeout(function () { m.focus({ preventScroll: true }); }, 0);
    });
  }

  // 初始化：桌面預設展開；首頁一律展開，不讓舊的收合狀態綁住入口
  pinned = readStr(SIDE_KEY) !== 'collapsed';
  if (document.body.classList.contains('page-home')) pinned = true;
  initReadTools();
  initLabelFilters();
  syncNav();
  loadTree();

  if (toggle) toggle.addEventListener('click', toggleNav);
  if (closeBtn) closeBtn.addEventListener('click', function () { closeDrawer(true); });
  if (scrim) scrim.addEventListener('click', function () { closeDrawer(true); });
  var collapseBtn = document.getElementById('navcollapse');
  if (collapseBtn) collapseBtn.addEventListener('click', function () {
    if (isMobile()) {
      closeDrawer(false);
    } else {
      setPinned(false, true);
      if (toggle) toggle.focus();
    }
  });

  // 左緣 peek：hover／focus 就露出側欄，不必先找按鈕
  if (edge) {
    edge.addEventListener('mouseenter', openPeek);
    edge.addEventListener('mouseleave', function () { if (peeking) closePeek(180); });
    edge.addEventListener('focus', openPeek);
    edge.addEventListener('click', function () {
      setPinned(true, true);
      if (toggle) toggle.focus();
    });
  }
  if (nav) {
    nav.addEventListener('mouseenter', function () { clearTimeout(peekTimer); });
    nav.addEventListener('mouseleave', function () { if (peeking) closePeek(180); });
    nav.addEventListener('focusin', function () { if (peeking) clearTimeout(peekTimer); });
    nav.addEventListener('focusout', function () { if (peeking) closePeek(200); });
  }

  document.addEventListener('pointerdown', function (e) {
    if (!peeking) return;
    if (nav && nav.contains(e.target)) return;
    if (edge && edge.contains(e.target)) return;
    closePeek(0);
  });

  document.addEventListener('keydown', function (e) { trapFocus(e); globalKey(e); });

  function onModeChange() {
    if (isMobile()) {
      peeking = false;
      drawerOpen = false;
    } else {
      drawerOpen = false;
      peeking = false;
      pinned = readStr(SIDE_KEY) !== 'collapsed';
      if (document.body.classList.contains('page-home')) pinned = true;
    }
    syncNav();
  }
  if (isMobileQuery) {
    if (isMobileQuery.addEventListener) isMobileQuery.addEventListener('change', onModeChange);
    else if (isMobileQuery.addListener) isMobileQuery.addListener(onModeChange);
  }

  window.addEventListener('resize', function () {
    var bar = document.querySelector('.tb-readtools');
    if (bar) syncReadButtons(bar);
  });

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
    else if (peeking) { peeking = false; syncNav(); }
  });

  window.addEventListener('hashchange', function () { setTimeout(jumpToHash, 0); });
  // 長頁（合編可達 30 萬 px）載入初期版面可能還在變動：load 後再校正，
  // 900ms 後若使用者還沒自己捲動，再補一次，避免落在錯的段落。
  window.addEventListener('load', function () {
    setTimeout(jumpToHash, 0);
    setTimeout(function () { if (!userMoved) jumpToHash(); }, 900);
  });
  window.addEventListener('pageshow', function (e) {
    if (e.persisted && location.hash) setTimeout(jumpToHash, 0);
  });

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
