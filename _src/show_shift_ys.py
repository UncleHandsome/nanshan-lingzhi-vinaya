import os, io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))
g = lambda s: {han(s)[i:i+2] for i in range(len(han(s)) - 1)}
sc = lambda a, b: len(g(a) & g(b))

for k in ['01a_卷一之一', '13a_卷三之二', '16a_卷三之五']:
    sp = [x.strip() for x in io.open(os.path.join(B, 'TXT_分卷', '03_業疏', k + '.txt'), encoding='utf-8').read().split('\n')[5:] if x.strip()]
    tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(os.path.join(B, 'AI語譯', 'out', '03_業疏', k + '.txt'), encoding='utf-8').read()) if x.strip()]
    print('==', k)
    for i in range(min(len(sp), len(tt)) - 1):
        if sc(sp[i], tt[i + 1]) > max(8, sc(sp[i], tt[i]) * 1.6):
            print(i + 1, 'SP:', sp[i][:40])
            print('   TT[now]:', tt[i][:40])
            print('   TT[next]:', tt[i + 1][:40])
