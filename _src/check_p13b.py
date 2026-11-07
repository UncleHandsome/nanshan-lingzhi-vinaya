import glob, os, io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
for f in sorted(glob.glob(os.path.join(B, 'TXT_分卷', '01_行事鈔', '*.txt'))):
    k = os.path.basename(f)[:-4]
    if not re.match(r'^13', k):
        continue
    sp = [x.strip() for x in io.open(f, encoding='utf-8').read().split('\n')[5:] if x.strip()]
    tp = os.path.join(B, 'AI語譯', 'out', '01_行事鈔', k + '.txt')
    tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()] if os.path.exists(tp) else []
    print(k, 'sp', len(sp), 'tt', len(tt))
    for i in range(min(3, len(sp))):
        print('  ', i, sp[i][:30], '||', (tt[i][:30] if i < len(tt) else 'NA'))
