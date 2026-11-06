# -*- coding: utf-8 -*-
"""把篇11-30 材料分成 bounds/ 與 splits/ 兩個資料夾；篇14 分塊各自產生兩種版本"""
import io, os, re, json, shutil, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
ROOT = os.path.join(B, '會本材料_11-30')
BD = os.path.join(ROOT, 'bounds')
SD = os.path.join(ROOT, 'splits')
os.makedirs(BD, exist_ok=True)
os.makedirs(SD, exist_ok=True)

for p in range(11, 31):
    for kind, dst in (('bounds', BD), ('splits', SD)):
        src = os.path.join(ROOT, '篇%02d_%s.md' % (p, kind))
        if os.path.exists(src):
            shutil.move(src, os.path.join(dst, os.path.basename(src)))
print('moved per-篇 files')

# 篇14 分塊：重建 bounds / splits 兩種
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
SECS = ex.sections(); ZI = ex.build_zi(SECS, ex.zsecs())
AM = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))
SKIP = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇')
p = 14; idx = p - 1
sec = SECS[idx]; zi = ZI[idx]; am = AM.get(str(idx), [])
chao = [it[0] for it in sec['items'] if not SKIP.match(it[0].strip())]
N = len(zi); CH = 6; step = (N + CH - 1) // CH

T_B = """## 任務
為本塊範圍內每條鈔找出它的註釋從哪個記段開始（只針對記%04d–%04d）。
回傳 JSON：{"bounds":[{"c":%d,"n":%d}, ...]}
規則：c 連續、n 遞增、不確定取後一段。只回 JSON。"""

T_S = """## 任務
找出本塊記段中「跨兩鈔」者，標出切點（只針對記%04d–%04d）。
回傳 JSON：{"splits":[{"n":16,"base":4,"markers":["大界中"],"targets":[4,5]}]}
規則：marker 必須在該記段原文逐字出現；targets 從 base 起連續。只回 JSON。"""

for k in range(CH):
    a = k * step + 1
    b = min(N, (k + 1) * step)
    cs = [int(am[i - 1]) for i in range(a, b + 1) if i - 1 < len(am) and int(am[i - 1]) > 0]
    lo = max(1, (min(cs) if cs else 1) - 3)
    hi = min(len(chao), (max(cs) if cs else len(chao)) + 3)
    ch = '\n'.join('【鈔%03d】%s' % (i, chao[i - 1]) for i in range(lo, hi + 1))
    ji = '\n'.join('【記%04d】(c=%d) %s' % (i, int(am[i - 1]) if i - 1 < len(am) else 0, zi[i - 1][0])
                   for i in range(a, b + 1))
    head = """# 篇14 隨戒釋相（第%d塊，記%04d–%04d）

《四分律行事鈔》與《資持記》局部資料（鈔號為全域編號，只列本塊涉及範圍）。
只需處理【記%04d】到【記%04d】。

## 鈔（%d–%d）
%s

## 記（%d–%d）
%s

""" % (k + 1, a, b, a, b, lo, hi, ch, a, b, ji)
    for kind, dst, tmpl in (('bounds', BD, T_B % (a, b, lo, a)),
                            ('splits', SD, T_S % (a, b))):
        d2 = os.path.join(dst, '篇14_分塊')
        os.makedirs(d2, exist_ok=True)
        name = '第%d塊_記%04d-%04d_%s.md' % (k + 1, a, b, kind)
        io.open(os.path.join(d2, name), 'w', encoding='utf-8').write(head + tmpl)
print('p14 chunks regenerated in both folders')

# 移除舊的混合分塊資料夾
old = os.path.join(ROOT, '篇14_分塊')
if os.path.isdir(old):
    shutil.rmtree(old)
print('removed old mixed folder')
