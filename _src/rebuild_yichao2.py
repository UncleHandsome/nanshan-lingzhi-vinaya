# -*- coding: utf-8 -*-
"""義鈔：FIX用_終修、PASS用_終審，加長段，重建定稿。"""
import io, json, os, re, shutil
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
ROOT = os.path.join(B, '測試', '重譯', '義鈔')
LT = os.path.join(ROOT, '_長段')
raw = io.open(os.path.join(B, 'TXT', '05_四分律拾毗尼義鈔.txt'), encoding='utf-8').read()
h = ''
for c in raw:
    if '\u4e00' <= c <= '\u9fff':
        h += c

def han(s):
    s = re.sub(r'^(?:【[^】]+】)+', '', str(s).strip())
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))

def source_from_material(md):
    ms = list(re.finditer(r'■\s*[^\n（]*（原文）', md))
    if not ms:
        return ''
    s = md[ms[-1].end():].strip()
    cut = min([x for x in (s.find('【後文背景'), s.find('【裁決'), s.find('\n---')) if x >= 0] or [len(s)])
    return s[:cut].strip()

def term_translation(path):
    t = io.open(path, encoding='utf-8').read()
    j = t.rfind('【待審譯文】')
    if j < 0:
        return ''
    s = t[j + 6:].strip()
    cut = min([x for x in (s.find('【後文背景'), s.find('【裁決'), s.find('\n---')) if x >= 0] or [len(s)])
    return s[:cut].strip()

def clean_tr(tr):
    lines = [x for x in tr.strip().splitlines() if x.strip()]
    if lines and re.match(r'^【[^】]+】$', lines[0]):
        lines = lines[1:]
    return '\n'.join(lines).strip()

rows = []
# root
matdir = os.path.join(ROOT, '_材料')
termdir = os.path.join(ROOT, '_終審')
revdir = os.path.join(ROOT, '_終修', '回覆')
for f in sorted(os.listdir(matdir)):
    if not f.endswith('.md'):
        continue
    key = f[:-3]
    src = source_from_material(io.open(os.path.join(matdir, f), encoding='utf-8').read())
    if not src:
        continue
    rp = os.path.join(revdir, key + '_回.txt')
    if os.path.exists(rp):
        tr = io.open(rp, encoding='utf-8').read()
    else:
        tp = os.path.join(termdir, key + '.md')
        tr = term_translation(tp) if os.path.exists(tp) else ''
    tr = clean_tr(tr)
    if not tr:
        continue
    q = h.find(han(src)[:20])
    if q < 0:
        q = h.find(han(src)[:12])
    rows.append({'book': '義鈔', 'book_id': 'yichao', 'key': key, 'label': '鈔文', 'source': src,
                 'translation': tr, 'revised': os.path.exists(rp), 'segments': [{'label': '鈔文', 'source': src, 'translation': tr}],
                 'raw_start': q, 'raw_end': q + len(han(src)) if q >= 0 else -1, 'vol': '', 'chunk': ''})
# long
lmat = os.path.join(LT, '_材料')
lf = os.path.join(LT, '_定稿')
bykey = {}
for f in os.listdir(lmat):
    if f.endswith('.md'):
        k = re.sub(r'_\d+\.md$', '', f)
        bykey.setdefault(k, []).append(os.path.join(lmat, f))
for k, fs in sorted(bykey.items()):
    srcs = [source_from_material(io.open(x, encoding='utf-8').read()) for x in sorted(fs)]
    src = '\n'.join(x for x in srcs if x)
    fp = os.path.join(lf, k + '.txt')
    if not src or not os.path.exists(fp):
        continue
    tr = clean_tr(io.open(fp, encoding='utf-8').read())
    if not tr:
        continue
    q = h.find(han(src)[:20])
    if q < 0:
        q = h.find(han(src)[:12])
    rows.append({'book': '義鈔', 'book_id': 'yichao', 'key': 'L:' + k, 'label': '鈔文', 'source': src,
                 'translation': tr, 'revised': True, 'segments': [{'label': '鈔文', 'source': src, 'translation': tr}],
                 'raw_start': q, 'raw_end': q + len(han(src)) if q >= 0 else -1, 'vol': '', 'chunk': ''})
p = os.path.join(B, '定稿', 'yichao.jsonl')
if os.path.exists(p):
    shutil.copy(p, os.path.join(B, '定稿', '_舊_yichao.jsonl'))
io.open(p, 'w', encoding='utf-8').writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in rows)
print('rows', len(rows), 'located', sum(1 for r in rows if r['raw_start'] >= 0), 'long', sum(1 for r in rows if r['key'].startswith('L:')))
