import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))

def grams(s, n=2):
    h = han(s)
    return {h[i:i + n] for i in range(len(h) - n + 1)}

for k in ['05c_卷中之一', '06a_卷中之二']:
    sp = [x.strip() for x in io.open(os.path.join(B, 'TXT_分卷', '01_行事鈔', k + '.txt'), encoding='utf-8').read().split('\n')[5:] if x.strip()]
    tp = os.path.join(B, 'AI語譯', 'out', '01_行事鈔', k + '.txt')
    tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
    best, bk = -1, 0
    for sh in range(-3, 4):
        tot = 0
        for i in range(len(sp)):
            j = i + sh
            if 0 <= j < len(tt):
                tot += len(grams(sp[i]) & grams(tt[j]))
        if tot > best:
            best, bk = tot, sh
    print(k, 'shift', bk, 'score', best, 'len', len(sp), len(tt))
    if bk != 0:
        new = [tt[i + bk] if 0 <= i + bk < len(tt) else '' for i in range(len(sp))]
        io.open(tp, 'w', encoding='utf-8').write('\n\n'.join(new) + '\n')
        print(' applied', bk)
