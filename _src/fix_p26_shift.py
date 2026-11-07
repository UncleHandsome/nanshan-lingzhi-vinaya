import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))
g = lambda s: {han(s)[i:i + 2] for i in range(len(han(s)) - 1)}
sc = lambda a, b: len(g(a) & g(b))

sp = [x.strip() for x in io.open(os.path.join(B, 'TXT_分卷', '01_行事鈔', '12a_卷下之四.txt'), encoding='utf-8').read().split('\n')[5:] if x.strip()]
fp = os.path.join(B, 'AI語譯', 'out', '01_行事鈔', '12a_卷下之四.txt')
tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(fp, encoding='utf-8').read()) if x.strip()]
n = min(len(sp), len(tt))
# 找最好的「多出段」位置：移除 tt[k] 後整體對齊分數最高
base = sum(sc(sp[i], tt[i]) for i in range(n))
best_k, best = None, base
for k in range(len(tt)):
    cand = tt[:k] + tt[k + 1:]
    s = sum(sc(sp[i], cand[i]) for i in range(min(len(sp), len(cand))))
    if s > best:
        best, best_k = s, k
print('base', base, 'best_k', best_k, 'score', best)
if best_k is not None:
    tt.pop(best_k)
    io.open(fp, 'w', encoding='utf-8').write('\n\n'.join(tt) + '\n')
    print('已移除多餘段，len', len(tt))
