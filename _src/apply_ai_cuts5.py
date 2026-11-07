import io, os, json, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
ZI = ex.build_zi(ex.sections(), ex.zsecs())

def cmap_of(p):
    fp = os.path.join(B, 'AI語譯', '_work', 'pian_bounds', 'bounds_篇%02d.json' % p)
    bs = [(int(x['c']), int(x['n'])) for x in json.load(io.open(fp, encoding='utf-8-sig'))['bounds']]
    cm = {}
    for i, (c, n) in enumerate(bs):
        end = bs[i + 1][1] - 1 if i + 1 < len(bs) else 10 ** 6
        for k in range(n, max(n, end) + 1):
            cm[k] = c
    return cm

OPS = [
    (7, 7, ['化教，標中']),
    (7, 17, ['《涅槃》中']),
    (7, 31, ['正治，具緣中']),
    (27, 41, ['次科，《母論》', '第七']),
]
for p in sorted({o[0] for o in OPS}):
    fp = os.path.join(B, 'AI語譯', '_work', 'pian_manual', '篇%02d.json' % p)
    m = json.load(io.open(fp, encoding='utf-8-sig')) if os.path.exists(fp) else {'splits': []}
    ops = [o for o in OPS if o[0] == p]
    nums = {o[1] for o in ops}
    m['splits'] = [e for e in m.get('splits', []) if int(e['n']) not in nums]
    cm = cmap_of(p)
    for _, n, marks in ops:
        t = ZI[p - 1][n - 1][0]
        if not all(mk in t for mk in marks):
            print('MISS', p, n, marks); continue
        c = max(1, cm.get(n, 1))
        tg = list(range(c, c + len(marks) + 1))
        m['splits'].append({'n': n, 'base': c, 'markers': marks, 'targets': tg})
        print('篇%d 記%d %s → %s' % (p, n, marks, tg))
    json.dump(m, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# 篇14 52–60 戒：以 AI 排序重設 記951–974 的鈔號錨點
fp = os.path.join(B, 'AI語譯', '_work', 'pian_manual', '篇14.json')
m = {'splits': []}
if os.path.exists(fp):
    m = json.load(io.open(fp, encoding='utf-8-sig'))
anchors = {951: 222, 952: 223, 953: 224, 954: 225, 955: 225, 956: 226, 957: 226,
           958: 227, 959: 227, 960: 227, 961: 227, 962: 228, 963: 228, 964: 228,
           965: 229, 966: 229, 967: 230, 968: 231, 969: 231, 970: 231, 971: 231, 972: 231,
           973: 231, 974: 231}
m['splits'] = [e for e in m.get('splits', []) if int(e['n']) not in anchors]
for n, c in anchors.items():
    m['splits'].append({'n': n, 'base': c})
json.dump(m, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('篇14 錨點', len(anchors))
