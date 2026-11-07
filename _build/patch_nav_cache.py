import io, os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'

# 1) nav.js：更穩妥的錨點回復（多次重試 + hashchange）
p = os.path.join(B, '_src', 'nav.js')
s = io.open(p, encoding='utf-8').read()
old = """  // 目錄點擊後：等 nav 重建完再回到錨點，避免「重刷後跑掉」
  function restoreHash() {
    if (!location.hash) return;
    var el = document.getElementById(location.hash.slice(1));
    if (el) setTimeout(function () { el.scrollIntoView({ block: 'start' }); }, 60);
  }
  spy();
  restoreHash();"""
new = """  // 目錄點擊後：等 nav 重建完再回到錨點，避免「重刷後跑掉」
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
  window.addEventListener('hashchange', function () { setTimeout(jump, 0); setTimeout(jump, 200); });"""
if 'function jump()' not in s:
    s = s.replace(old, new)
    s = s.replace("fetch(root + 'nav.json')", "fetch(root + 'nav.json?v=3')")
    io.open(p, 'w', encoding='utf-8').write(s)
    print('nav.js patched')

# 2) 模板引用加版本號，避免瀏覽器快取舊 JS
for f in ['site2.py', 'site_hebian.py', 'build_appendix.py']:
    q = os.path.join(B, '_src', f)
    t = io.open(q, encoding='utf-8').read()
    if 'nav.js' in t and 'nav.js?v=' not in t:
        t = t.replace("'nav.js'", "'nav.js?v=3'").replace('"nav.js"', '"nav.js?v=3"')
        io.open(q, 'w', encoding='utf-8').write(t)
        print(f, 'script version added')
    elif 'nav.js?v=3' in t:
        print(f, 'already versioned')
