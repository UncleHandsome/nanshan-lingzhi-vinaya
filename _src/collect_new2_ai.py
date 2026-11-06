import io, os, glob, json, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = os.path.join(B, 'AI語譯', '_work', 'new2_ai')
rows = {}
for f in sorted(glob.glob(os.path.join(D, 'out_*.json'))):
    try:
        d = json.load(io.open(f, encoding='utf-8-sig'))
    except Exception as e:
        print('bad', f, e)
        continue
    m = re.search(r'篇(\d+)', os.path.basename(f))
    if not m:
        continue
    p = int(m.group(1))
    rows[p] = d.get('rows', [])
    print('篇%-3d rows %d' % (p, len(rows[p])))
json.dump(rows, io.open(os.path.join(B, 'AI語譯', '_work', 'new2_ai_all.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('篇數', len(rows), '總列', sum(len(v) for v in rows.values()))
