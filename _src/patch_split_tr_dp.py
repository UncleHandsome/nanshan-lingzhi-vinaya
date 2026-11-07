import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\mk_pian_split.py'
s = io.open(p, encoding='utf-8').read()

start = s.find('def split_tr(tr, src_parts):')
end = s.find('HDR = re.compile', start)
assert start > 0 and end > start
new = '''def split_tr(tr, src_parts):
    if len(src_parts) <= 1:
        return [tr]
    tr_s = _sents(tr)
    if not tr_s:
        return [''] * len(src_parts)
    total_src = sum(max(1, han(x)) for x in src_parts) or 1
    cum_tr, acc = [], 0
    for x in tr_s:
        acc += max(1, han(x))
        cum_tr.append(acc)
    total_tr = cum_tr[-1] if cum_tr else 1
    cuts, accs, prev = [], 0, 0
    for part in src_parts[:-1]:
        accs += max(1, han(part))
        target = accs / total_src
        best, bj = 1e9, prev
        for j in range(prev, len(tr_s)):
            r = cum_tr[j] / total_tr
            d = abs(r - target)
            if d < best:
                best, bj = d, j + 1
            if r > target + 0.15:
                break
        cuts.append(max(prev + 1, min(bj, len(tr_s) - (len(src_parts) - len(cuts) - 1))))
        prev = cuts[-1]
    parts, prev = [], 0
    for c in cuts:
        parts.append(''.join(tr_s[prev:c]))
        prev = c
    parts.append(''.join(tr_s[prev:]))
    while len(parts) < len(src_parts):
        parts.append('')
    # 尾句守衛：下一科導語不留在前片
    for i in range(len(parts) - 1):
        ss = [x for x in _sents(parts[i]) if x.strip()]
        if len(ss) >= 2:
            last = ss[-1].strip()
            if han(last) < 22 and ('部分' in last or last.rstrip('。').endswith('中')
                                   or last.rstrip('。').endswith('科')):
                parts[i] = ''.join(ss[:-1])
                parts[i + 1] = last + parts[i + 1]
    return parts


'''
s = s[:start] + new + s[end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('split_tr upgraded to char-based boundary')
