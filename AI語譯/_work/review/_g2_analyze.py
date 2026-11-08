import json, re, io

path = 'AI語譯/_work/review/report_re2.tsv'
rows = []
with io.open(path, encoding='utf-8-sig') as f:
    header = f.readline().rstrip('\n').split('\t')
    for line in f:
        line = line.rstrip('\n')
        if not line.strip():
            continue
        fields = line.split('\t')
        d = dict(zip(header, fields))
        if d.get('book') == '01_行事鈔':
            rows.append(d)

def parse_pairs(sug):
    pairs = []
    for m in re.finditer(r'改為', sug):
        pass
    # split by 」改為「
    if '」改為「' in sug:
        pre, post = sug.split('」改為「', 1)
        # A: after last 將「 or after last 「 before
        aidx = pre.rfind('「')
        if aidx != -1:
            A = pre[aidx+1:]
        else:
            A = None
        # B: up to last 」 in post
        bidx = post.rfind('」')
        B = post[:bidx] if bidx != -1 else post
        pairs.append((A, B))
    return pairs

for i, d in enumerate(rows):
    d['idx'] = i
    d['pairs'] = parse_pairs(d.get('suggestion',''))
    hits = []
    for (A,B) in d['pairs']:
        if A:
            hits.append(A in d['current'])
    d['hit'] = hits

with io.open('AI語譯/_work/review/_g2_rows.json','w',encoding='utf-8') as f:
    json.dump(rows, f, ensure_ascii=False, indent=1)

print(len(rows))
for d in rows:
    print(d['idx'], d['gid'], d['chunk'], d['seg'], d['level'], d['cls'], '| pairs=', len(d['pairs']), d['hit'], '| sug=', d['suggestion'][:60].replace('\t',' '))
