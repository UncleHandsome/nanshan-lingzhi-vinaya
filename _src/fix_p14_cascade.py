import io, os, re, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))
g = lambda s: {han(s)[i:i + 2] for i in range(len(han(s)) - 1)}
sc = lambda a, b: len(g(a) & g(b))

for f in glob.glob(os.path.join(B, 'TXT_分卷', '01_行事鈔', '*.txt')):
    k = os.path.basename(f)[:-4]
    sp = [x.strip() for x in io.open(f, encoding='utf-8').read().split('\n')[5:] if x.strip()]
    if not any(('水中戲' in x) or ('擊攊' in x) for x in sp):
        continue
    tp = os.path.join(B, 'AI語譯', 'out', '01_行事鈔', k + '.txt')
    tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
    n = min(len(sp), len(tt))
    base = sum(sc(sp[i], tt[i]) for i in range(n))
    best_k = None
    if len(tt) > len(sp):
        best = base
        for j in range(len(tt)):
            cand = tt[:j] + tt[j + 1:]
            s = sum(sc(sp[i], cand[i]) for i in range(min(len(sp), len(cand))))
            if s > best:
                best, best_k = s, j
    print(k, 'sp', len(sp), 'tt', len(tt), 'base', base, 'best_k', best_k, 'best', best if best_k is not None else '')
    if best_k is not None:
        tt.pop(best_k)
        io.open(tp, 'w', encoding='utf-8').write('\n\n'.join(tt) + '\n')
        print('  removed')
