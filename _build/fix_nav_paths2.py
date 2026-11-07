import io, os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'

# site2
q = os.path.join(B, '_src', 'site2.py')
t = io.open(q, encoding='utf-8').read()
t = t.replace("os.path.join(SITE, 'nav.js?v=3')", "os.path.join(SITE, 'nav.js')")
t = t.replace("""'<link rel="stylesheet" href="' + css + '"><script defer src="' + prefix + 'nav.js"></script></head><body><div class="wrap">'""",
              """'<link rel="stylesheet" href="' + css + '"><script defer src="' + prefix + 'nav.js?v=3"></script></head><body><div class="wrap">'""")
io.open(q, 'w', encoding='utf-8').write(t)
print('site2 fixed')

# site_hebian / appendix
for f in ['site_hebian.py', 'build_appendix.py']:
    q = os.path.join(B, '_src', f)
    t = io.open(q, encoding='utf-8').read()
    t = t.replace('src="../nav.js"', 'src="../nav.js?v=3"').replace('src="nav.js"', 'src="nav.js?v=3"')
    io.open(q, 'w', encoding='utf-8').write(t)
    print(f, 'script tag fixed')
