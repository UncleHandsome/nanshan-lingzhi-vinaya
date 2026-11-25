/* 閱讀增強 ui.js
 * 1) 字級調整（記憶於 localStorage）
 * 2) 目前所在篇名顯示於頂部列
 * 3) 回到頂端浮動鈕
 * 4) 段落錨點（滑過顯示 §，點擊複製本段連結）
 */
(function () {
  'use strict';
  var root = document.documentElement;
  var FS_KEY = 'dsh-fs';
  var MIN = 80, MAX = 170, STEP = 10, DEF = 100;

  function getFS() {
    var v = 0;
    try { v = parseInt(localStorage.getItem(FS_KEY) || '', 10); } catch (e) {}
    return (v >= MIN && v <= MAX) ? v : DEF;
  }
  function applyFS(pct) {
    root.style.setProperty('--fs', (18 * pct / 100).toFixed(1) + 'px');
    try { localStorage.setItem(FS_KEY, String(pct)); } catch (e) {}
    syncButtons(pct);
  }
  function syncButtons(pct) {
    var b;
    b = document.querySelector('[data-fs="reset"]');
    if (b) b.textContent = pct + '%';
    var dec = document.querySelector('[data-fs="dec"]');
    var inc = document.querySelector('[data-fs="inc"]');
    if (dec) dec.disabled = pct <= MIN;
    if (inc) inc.disabled = pct >= MAX;
  }
  applyFS(getFS());

  document.addEventListener('click', function (ev) {
    var t = ev.target.closest ? ev.target.closest('[data-fs]') : null;
    if (t) {
      var pct = getFS();
      var act = t.getAttribute('data-fs');
      if (act === 'inc') pct = Math.min(MAX, pct + STEP);
      else if (act === 'dec') pct = Math.max(MIN, pct - STEP);
      else pct = DEF;
      applyFS(pct);
      ev.preventDefault();
      return;
    }
    var anchor = ev.target.closest ? ev.target.closest('[data-copy-url]') : null;
    if (anchor) {
      var url = anchor.getAttribute('data-copy-url');
      copy(url);
      ev.preventDefault();
    }
  });

  function copy(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(toast, function () { fallback(text); });
    } else { fallback(text); }
  }
  function fallback(text) {
    var ta = document.createElement('textarea');
    ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); } catch (e) {}
    document.body.removeChild(ta);
    toast();
  }
  var toastEl = null, toastTimer = 0;
  function toast(msg) {
    if (!toastEl) {
      toastEl = document.createElement('div');
      toastEl.className = 'ui-toast';
      document.body.appendChild(toastEl);
    }
    toastEl.textContent = msg || '已複製本段連結';
    toastEl.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove('show'); }, 1600);
  }


  // ── 閱讀進度條 ─────────────────────────────────────────
  var bar = document.createElement('div');
  bar.className = 'ui-progress';
  document.body.appendChild(bar);
  function updateBar() {
    var h = document.documentElement;
    var max = h.scrollHeight - h.clientHeight;
    var pct = max > 0 ? (h.scrollTop || window.scrollY) / max * 100 : 0;
    bar.style.width = Math.max(0, Math.min(100, pct)) + '%';
  }

  // ── 篇內小目錄（h2/h3）──────────────────────────────────
  var toc = null, tocBtn = null;
  function buildToc() {
    var items = [];
    var nodes = document.querySelectorAll('h2.sec, h3.sub, h2.sec + h3, .content h3');
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      var txt = (el.textContent || '').trim();
      if (!txt) continue;
      if (!el.id) el.id = 'sec-' + i;
      items.push({ id: el.id, text: txt, level: el.tagName === 'H2' ? 1 : 2 });
    }
    if (items.length < 3) return;
    toc = document.createElement('nav');
    toc.className = 'ui-toc';
    toc.setAttribute('aria-label', '篇內目錄');
    var h = '<div class="ui-toc-h">篇內目錄</div>';
    for (var j = 0; j < items.length; j++) {
      h += '<a class="lv' + items[j].level + '" href="#' + items[j].id + '">' +
           escU(items[j].text) + '</a>';
    }
    toc.innerHTML = h;
    document.body.appendChild(toc);
    tocBtn = document.createElement('button');
    tocBtn.type = 'button';
    tocBtn.className = 'ui-tocbtn';
    tocBtn.title = '篇內目錄';
    tocBtn.setAttribute('aria-label', '開合篇內目錄');
    tocBtn.textContent = '☰';
    tocBtn.addEventListener('click', function () { toc.classList.toggle('open'); });
    document.body.appendChild(tocBtn);
  }
  function escU(s) {
    return s.replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  // ── 鍵盤：j 下一篇 / k 上一篇 / t 目錄 ────────────────────
  function navByKey(dir) {
    var sel = dir > 0
      ? '.pager a[rel~="next"], .pager .next a, a.pager-next'
      : '.pager a[rel~="prev"], .pager .prev a, a.pager-prev';
    var a = document.querySelector(sel);
    if (!a) {
      var links = document.querySelectorAll('.pager a');
      for (var i = 0; i < links.length; i++) {
        var tx = links[i].textContent || '';
        if (dir > 0 && /下一/.test(tx)) { a = links[i]; break; }
        if (dir < 0 && /上一/.test(tx)) { a = links[i]; break; }
      }
    }
    if (a && a.href) location.href = a.href;
  }
  document.addEventListener('keydown', function (ev) {
    if (ev.ctrlKey || ev.metaKey || ev.altKey) return;
    var tag = (ev.target.tagName || '').toLowerCase();
    if (tag === 'input' || tag === 'textarea' || ev.target.isContentEditable) return;
    var k = ev.key;
    if (k === 'j') { navByKey(1); ev.preventDefault(); }
    else if (k === 'k') { navByKey(-1); ev.preventDefault(); }
    else if (k === 't' && toc) { toc.classList.toggle('open'); ev.preventDefault(); }
  });


  // ── 頁面右上角的大下載鈕 ───────────────────────────────
  function addDownloadCta() {
    if (/download\.html?$/.test(location.pathname)) return;
    var h1 = document.querySelector('main h1');
    if (!h1) return;
    var a = document.createElement('a');
    a.className = 'ui-dl-inline';
    a.href = 'download.html';
    a.textContent = '⬇ 下載 Word／PDF';
    a.title = '下載六書白話對照本（Word／PDF）';
    h1.parentNode.insertBefore(a, h1);
  }

  // ── 目前篇名 + 回到頂端 ────────────────────────────────
  var secs = [], nowEl = null;
  function init() {
    secs = Array.prototype.slice.call(document.querySelectorAll('h2.sec'));
    var crumb = document.querySelector('.tb-crumb');
    if (crumb) {
      nowEl = document.createElement('span');
      nowEl.className = 'tb-now';
      nowEl.setAttribute('aria-live', 'polite');
      crumb.appendChild(nowEl);
    }
    addDownloadCta();
    buildToc();
    onScroll();
    updateBar();
  }

  var tick = false;
  function onScroll() {
    if (tick) return;
    tick = true;
    requestAnimationFrame(function () {
      tick = false;
      var y = window.scrollY || document.documentElement.scrollTop || 0;
      updateBar();
      if (nowEl) {
        // 「目前篇名」判定的門檻＝頂部列實際高度
        var base = 45;
        var bar = document.querySelector('.topbar');
        if (bar) base = bar.getBoundingClientRect().height;
        base += 30;
        var cur = '';
        for (var i = 0; i < secs.length; i++) {
          var r = secs[i].getBoundingClientRect();
          if (r.top <= base) cur = secs[i].textContent; else break;
        }
        if (nowEl.textContent !== cur) nowEl.textContent = cur;
      }
    });
  }
  window.addEventListener('scroll', onScroll, { passive: true });

  // ── 段落錨點 § 已移除（浮動標記點不到、且會壓到版面）────────
  // 複製連結改由頂部列的「複製」按鈕（nav.js 綁定）提供。

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else { init(); }
})();
