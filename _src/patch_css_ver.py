import io, os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
for f in ['site2.py', 'site_hebian.py', 'build_appendix.py']:
    p = os.path.join(B, '_src', f)
    s = io.open(p, encoding='utf-8').read()
    s2 = s.replace('style.css?v=8', 'style.css?v=9').replace('style.css?v=7', 'style.css?v=9')
    if s2 != s:
        io.open(p, 'w', encoding='utf-8').write(s2)
        print(f, 'css version bumped')
    else:
        print(f, 'no change')
