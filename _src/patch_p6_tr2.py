import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_p6_huiben.py'
s = io.open(p, encoding='utf-8').read()

start = s.find('def split_tr(')
end = s.find('# 切好所有記段')
assert start > 0 and end > start
new = '''def _sents(x):
    out = re.findall(r'[^。！？；]*[。！？；]?', x)
    return [y for y in out if y.strip()]


def _align(ls, lt):
    """單調對齊：回傳 src 句索引 → tr 句索引"""
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
    mp = [0] * (n + 1)
    i, j = n, m
    while i > 0 or j > 0:
        pi, pj = bk[i][j]
        if pi == i - 1 and pj == j - 1:
            mp[i] = j - 1
        i, j = pi, pj
    last = 0
    for k in range(n + 1):
        mp[k] = max(mp[k], last)
        last = mp[k]
    return mp


han = lambda s: len(re.findall(r'[\\u4e00-\\u9fff]', s))


def split_tr(tr, src_parts):
    """依原文段落切點，把白話切到同樣段數（句對句單調對齊）"""
    src_s, tr_s = [], _sents(tr)
    for part in src_parts:
        src_s += _sents(part)
    if len(src_parts) <= 1:
        return [tr]
    mp = _align([max(1, han(x)) for x in src_s], [max(1, han(x)) for x in tr_s])
    cuts = []
    acc = 0
    for part in src_parts[:-1]:
        acc += len(_sents(part))
        j = mp[min(acc, len(mp) - 1)]
        cuts.append(j)
    cuts = sorted(set(max(1, min(j, len(tr_s))) for j in cuts))
    while len(cuts) < len(src_parts) - 1:
        cuts.append(min(len(tr_s) - 1, (cuts[-1] if cuts else 0) + 1))
    cuts = sorted(set(cuts))[:len(src_parts) - 1]
    parts, prev = [], 0
    for c in cuts:
        parts.append(''.join(tr_s[prev:c]))
        prev = c
    parts.append(''.join(tr_s[prev:]))
    while len(parts) < len(src_parts):
        parts.append('')
    return parts


'''
s = s[:start] + new + s[end:]
# 呼叫端改參數
s = s.replace("        w = [han(p) for p in ps]\n        ts = split_tr(t, w)", "        ts = split_tr(t, ps)")
io.open(p, 'w', encoding='utf-8').write(s)
print('split_tr sentence-aligned')
