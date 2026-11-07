import io, os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
q = os.path.join(B, '_src', 'nav.js')
s = io.open(q, encoding='utf-8').read()

add = '''
  // 同頁錨點：自己處理，避免瀏覽器重新載入造成「重刷」
  box.addEventListener('click', function (e) {
    var a = e.target.closest ? e.target.closest('a') : null;
    if (!a) return;
    var href = a.getAttribute('href') || '';
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
'''
if '同頁錨點' not in s:
    s = s.replace('  spy();\n  restoreHash();', add + '  spy();\n  restoreHash();')
    s = s.replace('nav.json?v=4', 'nav.json?v=5')
    io.open(q, 'w', encoding='utf-8').write(s)
    print('nav.js click handler added')

for f in ['site2.py', 'site_hebian.py', 'build_appendix.py']:
    p = os.path.join(B, '_src', f)
    t = io.open(p, encoding='utf-8').read().replace('nav.js?v=4', 'nav.js?v=5')
    io.open(p, 'w', encoding='utf-8').write(t)
print('templates v5')
