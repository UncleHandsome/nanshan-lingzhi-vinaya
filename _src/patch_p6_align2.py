import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_p6_huiben.py'
lines = io.open(p, encoding='utf-8').read().split('\n')
# 取代 _align（137-183 行，1-based 137 到 183）與 cut 行
start = next(i for i, l in enumerate(lines) if l.startswith('def _align('))
end = next(i for i, l in enumerate(lines) if l.startswith('def split_tr('))
new_align = '''def _align(ls, lt):
    n, m = len(ls), len(lt)
    if n == 0 or m == 0:
        return [0] * n
    ms = sum(ls) / n
    mt = sum(lt) / m
    INF = 1e9
    dp = [[INF] * (m + 1) for _ in range(n + 1)]
    bk = [[None] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0
    for i in range(n + 1):
        for j in range(m + 1):
            if i == 0 and j == 0:
                continue
            best, b = INF, None
            if i:
                v = dp[i - 1][j] + 0.6
                if v < best:
                    best, b = v, (i - 1, j)
            if j:
                v = dp[i][j - 1] + 0.6
                if v < best:
                    best, b = v, (i, j - 1)
            if i and j:
                v = dp[i - 1][j - 1] + abs(ls[i - 1] / ms - lt[j - 1] / mt)
                if v < best:
                    best, b = v, (i - 1, j - 1)
            dp[i][j] = best
            bk[i][j] = b
    pair = {}
    i, j = n, m
    while i > 0 or j > 0:
        pi, pj = bk[i][j]
        if pi == i - 1 and pj == j - 1:
            pair[i - 1] = j - 1
        i, j = pi, pj
    out = [None] * n
    for k in range(n):
        if k in pair:
            out[k] = pair[k]
    nxt = None
    for k in range(n - 1, -1, -1):
        if out[k] is None:
            out[k] = nxt
        else:
            nxt = out[k]
    last = 0
    for k in range(n):
        if out[k] is None:
            out[k] = last
        out[k] = max(out[k], last)
        last = out[k]
    return out

'''
lines = lines[:start] + new_align.split('\n') + lines[end:]
# 修正切點
for i, l in enumerate(lines):
    if 'j = mp[min(acc + 1, len(mp) - 1)]' in l:
        lines[i] = l.replace('mp[min(acc + 1, len(mp) - 1)]', 'mp[min(acc, len(mp) - 1)]')
io.open(p, 'w', encoding='utf-8').write('\n'.join(lines))
print('align replaced')
