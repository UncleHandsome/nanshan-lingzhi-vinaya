# -*- coding: utf-8 -*-
"""移除 docs/nicao 舊譯補洞；能從 _終審/_定稿 找到新譯才保留。"""
import io, json, os, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
ROOT = os.path.join(B, '測試', '重譯', '尼鈔')
raw = io.open(os.path.join(B, 'TXT', '04_四分律比丘尼鈔.txt'), encoding='utf-8').read()
h = ''
for c in raw:
    if '\u4e00' <= c <= '\u9fff':
        h += c

def han(s):
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))

def source_block(md):
    m = re.search(r'■\s*[^\n（]*（原文）', md)
    if not m:
        return ''
    s = md[m.end():].strip()
    cut = re.search(r'【待審譯文】|【裁決|【後文背景】|\n■\s*[^\n（]*（|\n---', s)
    if cut:
        s = s[:cut.start()].strip()
    return s

texts = []
td = os.path.join(ROOT, '_終審')
for f in os.listdir(td):
    if not f.endswith('.md'):
        continue
    k = f[:-3]
    md = io.open(os.path.join(td, f), encoding='utf-8').read()
    s = source_block(md)
    if s:
        texts.append((k, han(s), md))
p = os.path.join(B, '定稿', 'nicao.jsonl')
rows = [json.loads(x) for x in io.open(p, encoding='utf-8') if x.strip()]
keep = []
replaced = removed = 0
for r in rows:
    if not r['key'].startswith('GAP'):
        keep.append(r)
        continue
    g = han(r.get('source', ''))
    hit = next(((k, s, md) for k, s, md in texts if g[:16] in s or s[:16] in g), None)
    if not hit:
        removed += 1
        continue
    k, s, md = hit
    tr = ''
    fp = os.path.join(ROOT, '_定稿', k + '.txt')
    if os.path.exists(fp):
        tr = io.open(fp, encoding='utf-8').read()
    if not tr:
        j = md.rfind('【待審譯文】')
        if j >= 0:
            tr = md[j + 6:].strip()
    lines = [x for x in tr.splitlines() if x.strip()]
    if lines and re.match(r'^【[^】]+】$', lines[0]):
        lines = lines[1:]
    tr = '\n'.join(lines).strip()
    if not tr:
        removed += 1
        continue
    r['key'] = 'NEW:' + k
    r['source'] = s
    r['translation'] = tr
    r['revised'] = True
    r['segments'] = [{'label': '鈔文', 'source': s, 'translation': tr}]
    r['raw_start'] = h.find(s[:20])
    r['raw_end'] = r['raw_start'] + len(s) if r['raw_start'] >= 0 else -1
    keep.append(r)
    replaced += 1
io.open(p, 'w', encoding='utf-8').writelines(json.dumps(r, ensure_ascii=False) + '\n' for r in keep)
print('rows', len(rows), 'keep', len(keep), 'replaced', replaced, 'removed', removed)
