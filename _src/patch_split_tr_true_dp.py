import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

start = s.find('def split_tr(tr, src_parts):')
end = s.find('HDR = re.compile', start)
assert start > 0 and end > start
new = '''def split_tr(tr, src_parts):
    """句子級單調對齊：以句長比例做 DP，切點落在譯文句界。"""
    if len(src_parts) <= 1:
        return [tr]
    tr_s = _sents(tr)
    if len(tr_s) < len(src_parts):
        return [''] * len(src_parts)

    src_s, part_end = [], []
    for part in src_parts:
        ss = _sents(part)
        src_s += ss
        part_end.append(len(src_s))
    if not src_s:
        return [''] * len(src_parts)

    ms = sum(max(1, han(x)) for x in src_s) / len(src_s)
    mt = sum(max(1, han(x)) for x in tr_s) / len(tr_s)
    ns, nt = len(src_s), len(tr_s)
    INF = 1e9
    dp = [[INF] * (nt + 1) for _ in range(ns + 1)]
    bk = [[0] * (nt + 1) for _ in range(ns + 1)]
    dp[0][0] = 0
    for i in range(ns + 1):
        for j in range(nt + 1):
            if i == 0 and j == 0:
                continue
            best, arg = INF, 0
            if i and j:
                c = dp[i - 1][j - 1] + abs(max(1, han(src_s[i - 1])) / ms - max(1, han(tr_s[j - 1])) / mt)
                if c < best:
                    best, arg = c, 1
            if j:
                c = dp[i][j - 1] + 0.6
                if c < best:
                    best, arg = c, 2
            if i:
                c = dp[i - 1][j] + 0.6
                if c < best:
                    best, arg = c, 3
            dp[i][j] = best
            bk[i][j] = arg
    # 對每個部分結尾，找最佳 j
    bounds = []
    for k, se in enumerate(part_end[:-1]):
        bestj = None
        for j in range(1, nt):
            if bestj is None or dp[se][j] < dp[se][bestj]:
                bestj = j
        bounds.append(max(1, min(bestj, nt - (len(part_end) - 1 - k))))
    bounds.append(nt)
    # 保證遞增
    for i in range(1, len(bounds)):
        bounds[i] = max(bounds[i], bounds[i - 1] + 1)
    bounds[-1] = nt
    parts, prev = [], 0
    for b in bounds:
        parts.append(''.join(tr_s[prev:b]))
        prev = b
    while len(parts) < len(src_parts):
        parts.append('')
    return parts


'''
s = s[:start] + new + s[end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('split_tr DP installed')
