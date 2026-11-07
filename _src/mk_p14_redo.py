# -*- coding: utf-8 -*-
"""篇14 重新出題：10 塊，每塊含 bounds+splits 兩份提示（資料內嵌）"""
import io, os, re, json, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
SECS = ex.sections(); ZI = ex.build_zi(ex.sections(), ex.zsecs())
AM = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))
SKIP = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇')
p = 14
idx = p - 1
sec = SECS[idx]; zi = ZI[idx]; am = AM.get(str(idx), [])
chao = [it[0] for it in sec['items'] if not SKIP.match(it[0].strip())]
N = len(zi); CH = 10
step = (N + CH - 1) // CH
OUT = os.path.join(B, '會本材料_11-30', '篇14_重出')
os.makedirs(OUT, exist_ok=True)

B_TAIL = """
## 任務（鈔界）
為本塊鈔號範圍（c=%d..%d）的每一條鈔，找出「它的註釋從哪一個記段開始」。
回傳 JSON：{"bounds":[{"c":%d,"n":1}, ...]}
規則：c 連續、n 遞增、不確定取後一段；只回 JSON。
"""
S_TAIL = """
## 任務（切點）
找出本塊記段中「跨兩鈔」者，標出切點（只針對記%04d–%04d）。
回傳 JSON：{"splits":[{"n":16,"base":4,"markers":["X中"],"targets":[4,5]}]}
規則：marker 必須在該記段原文逐字出現；targets 從 base 起連續；不確定不要列。只回 JSON。
"""

for k in range(CH):
    a = k * step + 1
    b = min(N, (k + 1) * step)
    cs = [int(am[i - 1]) for i in range(a, b + 1) if i - 1 < len(am) and int(am[i - 1]) > 0]
    lo = max(1, (min(cs) if cs else 1) - 2)
    hi = min(len(chao), (max(cs) if cs else len(chao)) + 2)
    ch = '\n'.join('【鈔%03d】%s' % (i, chao[i - 1]) for i in range(lo, hi + 1))
    ji = '\n'.join('【記%04d】%s' % (i, zi[i - 1][0]) for i in range(a, b + 1))
    head = """# 篇14 隨戒釋相（第%d/10 塊，記%04d–%04d）

《四分律行事鈔》與《資持記》局部資料。鈔號為全域編號，只列本塊涉及範圍；記段只列本塊。

## 鈔（%d–%d）
%s

## 記（%d–%d）
%s
""" % (k + 1, a, b, lo, hi, ch, a, b, ji)
    io.open(os.path.join(OUT, '第%02d塊_記%04d-%04d_bounds.md' % (k + 1, a, b)), 'w', encoding='utf-8').write(
        head + B_TAIL % (lo, hi, lo))
    io.open(os.path.join(OUT, '第%02d塊_記%04d-%04d_splits.md' % (k + 1, a, b)), 'w', encoding='utf-8').write(
        head + S_TAIL % (a, b))
    print('第%02d塊 記%d-%d 鈔%d-%d 字數%d' % (k + 1, a, b, lo, hi, len(head)))
