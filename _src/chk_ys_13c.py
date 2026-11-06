import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
T = os.path.join(B, 'AI語譯', 'out', '03_業疏')
k = '13a_卷三之二'
tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(os.path.join(T, k + '.txt'), encoding='utf-8').read()) if x.strip()]
for i, t in enumerate(tt):
    if '授戒' in t or '標其目' in t or '標舉其目' in t:
        print(i, '|', t[:60])
