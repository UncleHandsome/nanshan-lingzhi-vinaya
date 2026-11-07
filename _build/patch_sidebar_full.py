import io, os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'

# A. CSS：取消平滑捲動、錨點預留位移
p = os.path.join(B, 'docs', 'style.css')
c = io.open(p, encoding='utf-8').read()
if 'scroll-behavior:smooth' in c:
    c = c.replace('scroll-behavior:smooth', 'scroll-behavior:auto')
if '.sec{scroll-margin' not in c:
    c += '''
/* 錨點定位：避免被上方內容遮住 */
h2.sec, span[id^="p"]{scroll-margin-top:14px}
'''
io.open(p, 'w', encoding='utf-8').write(c)
print('css patched')

# B. nav.js：跳到錨點時強制 instant，版本升 v4
q = os.path.join(B, '_src', 'nav.js')
s = io.open(q, encoding='utf-8').read()
s = s.replace("""  function jump() {
    if (!location.hash) return;
    var el = document.getElementById(location.hash.slice(1));
    if (el) el.scrollIntoView({ block: 'start', behavior: 'auto' });
  }""",
"""  function jump() {
    if (!location.hash) return;
    var el = document.getElementById(location.hash.slice(1));
    if (!el) return;
    var de = document.documentElement;
    var old = de.style.scrollBehavior;
    de.style.scrollBehavior = 'auto';
    el.scrollIntoView({ block: 'start', behavior: 'instant' });
    de.style.scrollBehavior = old;
  }""")
s = s.replace("nav.json?v=3", "nav.json?v=4")
io.open(q, 'w', encoding='utf-8').write(s)
print('nav.js patched')

# C. 戒疏：濾掉過短的【序】行（如「佛日日日新。」）
r = os.path.join(B, '_src', 'toc_rules.py')
t = io.open(r, encoding='utf-8').read()
old = """    if book == 'jieshu':
        if t.startswith('【序】'):
            return True"""
new = """    if book == 'jieshu':
        if t.startswith('【序】'):
            body = re.sub(r'^【序】\\s*', '', t)
            return len(re.findall(r'[\\u4e00-\\u9fff]', body)) >= 6"""
if old in t:
    t = t.replace(old, new)
    io.open(r, 'w', encoding='utf-8').write(t)
    print('jieshu 序文 filter')

# D. 模板 script 版本升 v4
for f in ['site2.py', 'site_hebian.py', 'build_appendix.py']:
    q2 = os.path.join(B, '_src', f)
    x = io.open(q2, encoding='utf-8').read().replace('nav.js?v=3', 'nav.js?v=4')
    io.open(q2, 'w', encoding='utf-8').write(x)
print('templates v4')
