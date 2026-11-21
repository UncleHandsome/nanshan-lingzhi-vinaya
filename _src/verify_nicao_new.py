# -*- coding: utf-8 -*-
"""尼鈔：新 nicao.jsonl 的完整驗證（結構、內容、與舊檔比對）。"""
import io, json, os, re, collections
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
raw = io.open(os.path.join(B, 'TXT', '04_四分律比丘尼鈔.txt'), encoding='utf-8').read()
h = ''
for c in raw:
    if '\u4e00' <= c <= '\u9fff':
        h += c


def han(s):
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))


new = [json.loads(x) for x in io.open(os.path.join(B, '定稿', 'nicao.jsonl'), encoding='utf-8') if x.strip()]
old = [json.loads(x) for x in io.open(os.path.join(B, '定稿', '_舊_nicao.jsonl'), encoding='utf-8') if x.strip()]
print('new', len(new), 'old', len(old))

# 1 結構
fields = {'book', 'book_id', 'key', 'label', 'source', 'translation', 'revised', 'segments', 'raw_start', 'raw_end', 'vol', 'chunk'}
bad = [r['key'] for r in new if set(r) != fields]
print('field mismatch', bad[:10], len(bad))
print('labels', collections.Counter(r['label'] for r in new))
print('revised', sum(1 for r in new if r['revised']))
print('vol/chunk', collections.Counter((r['vol'], r['chunk']) for r in new))
print('key uniq', len(set(r['key'] for r in new)))
print('keys missing 1..778', sorted(set(str(i) for i in range(1, 779)) - set(r['key'] for r in new)))
print('GAP keys', [r['key'] for r in new if r['key'].startswith('GAP')])

# 2 原文自洽
bad_src = []
for r in new:
    a, b = r['raw_start'], r['raw_end']
    if han(r['source']) != h[a:b]:
        bad_src.append((r['key'], a, b, len(han(r['source'])), b - a))
print('source != raw slice', bad_src[:10], len(bad_src))

# 3 譯文
bad_tr = []
for r in new:
    t = r['translation']
    if not t.strip():
        bad_tr.append((r['key'], 'empty'))
    for pat in ('【裁決', '【後文背景', '【原文】', '待審譯文', '###', '■', '【修訂譯文】', '【逐句'):
        if pat in t:
            bad_tr.append((r['key'], pat))
print('translation suspicious', bad_tr[:20], len(bad_tr))
seg_bad = [r['key'] for r in new if r['segments'][0]['translation'] != re.sub(r'^【[^】]+】\s*', '', r['translation'].strip()).strip()]
print('segment translation mismatch', seg_bad[:10], len(seg_bad))
seg_bad2 = [r['key'] for r in new if r['segments'][0]['source'] != r['source'] or r['segments'][0]['label'] != r['label']]
print('segment src/label mismatch', seg_bad2[:10], len(seg_bad2))

# 4 與舊檔比對
oldmap = {r['key']: r for r in old}
same = diff = 0
diffkeys = []
for r in new:
    o = oldmap.get(r['key'])
    if not o:
        continue
    if o['translation'].strip() == r['translation'].strip() and o['source'] == r['source']:
        same += 1
    else:
        diff += 1
        diffkeys.append(r['key'])
print('common same', same, 'diff', diff)
print('diff keys', diffkeys[:40])
newkeys = set(r['key'] for r in new)
print('old keys not in new', sorted(set(oldmap) - newkeys))
print('new keys added', sorted(newkeys - set(oldmap)))
