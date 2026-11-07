import glob, os, io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))
for f in sorted(glob.glob(os.path.join(B, 'TXT_分卷', '03_業疏', '*.txt'))):
    k = os.path.basename(f)[:-4]
    sp = [x.strip() for x in io.open(f, encoding='utf-8').read().split('\n')[5:] if x.strip()]
    tp = os.path.join(B, 'AI語譯', 'out', '03_業疏', k + '.txt')
    tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
    for i in range(min(len(sp), len(tt))):
        if len(han(tt[i])) < 5:
            print(k, i + 1, '| 原:', sp[i][:60], '| 譯:', repr(tt[i][:20]))
