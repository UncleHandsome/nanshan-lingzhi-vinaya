import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '03_業疏')
for f in ['19b_卷四之二.txt', '20a_卷四之三.txt', '20b_卷四之三.txt', '22a_卷四之五.txt']:
    p = os.path.join(S, f)
    if not os.path.exists(p):
        continue
    sp = [x.strip() for x in io.open(p, encoding='utf-8').read().split('\n')[5:] if x.strip()]
    print('=====', f, len(sp))
    for i, x in enumerate(sp[:40], 1):
        print('%3d | %s' % (i, x[:60]))
