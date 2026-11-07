import io, os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
for f in ['site2.py', 'site_hebian.py', 'build_appendix.py']:
    q = os.path.join(B, '_src', f)
    t = io.open(q, encoding='utf-8').read()
    # 修正被誤改的檔案來源路徑
    t = t.replace("os.path.join(B, '_src', 'nav.js?v=3')", "os.path.join(B, '_src', 'nav.js')")
    io.open(q, 'w', encoding='utf-8').write(t)
    print(f, 'source path fixed')
