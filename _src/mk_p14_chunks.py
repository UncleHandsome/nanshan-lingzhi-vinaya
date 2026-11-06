# -*- coding: utf-8 -*-
"""篇14 分塊提示檔（6 塊）與使用說明"""
import io, os, re, json, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
SECS = ex.sections(); ZI = ex.build_zi(SECS, ex.zsecs())
AM = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))
SKIP = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇')
OUT = os.path.join(B, '會本材料_11-30', '篇14_分塊')
os.makedirs(OUT, exist_ok=True)

p = 14
idx = p - 1
sec = SECS[idx]; zi = ZI[idx]; am = AM.get(str(idx), [])
chao = [it[0] for it in sec['items'] if not SKIP.match(it[0].strip())]
N = len(zi)
CH = 6
step = (N + CH - 1) // CH
for k in range(CH):
    a = k * step + 1
    b = min(N, (k + 1) * step)
    cs = [int(am[i - 1]) for i in range(a, b + 1) if i - 1 < len(am) and int(am[i - 1]) > 0]
    lo = max(1, (min(cs) if cs else 1) - 3)
    hi = min(len(chao), (max(cs) if cs else len(chao)) + 3)
    ch = '\n'.join('【鈔%03d】%s' % (i, chao[i - 1]) for i in range(lo, hi + 1))
    ji = '\n'.join('【記%04d】(c=%d) %s' % (i, int(am[i - 1]) if i - 1 < len(am) else 0, zi[i - 1][0])
                   for i in range(a, b + 1))
    head = """# 會本標註：篇14 隨戒釋相（第%d塊，記%04d–%04d）

你是律學古籍校勘專家。這是《四分律行事鈔》與《資持記》的局部資料（鈔號為全域編號，只列本塊涉及的範圍）。
只需針對【記%04d】到【記%04d】這些記段作答，其他記段不要處理。

## 鈔（全域編號 %d–%d）
%s

## 記（%d–%d）
%s

## 任務
請分別回傳兩份 JSON（先 bounds、再 splits），格式如下。

bounds：每條鈔（本塊範圍內）從哪個記段開始
```json
{"bounds": [{"c": %d, "n": %d}, ...]}
```

splits：跨鈔記段的切點（marker 必須逐字存在於該記段；targets 從 base 起連續）
```json
{"splits": [{"n": 16, "base": 4, "markers": ["大界中"], "targets": [4, 5]}]}
```

只回這兩份 JSON，不要解釋。
""" % (k + 1, a, b, a, b, lo, hi, ch, a, b, ji, lo, a)
    io.open(os.path.join(OUT, '第%d塊_記%04d-%04d.md' % (k + 1, a, b)), 'w', encoding='utf-8').write(head)
    print('塊%d 記%d-%d 鈔%d-%d 字數%d' % (k + 1, a, b, lo, hi, len(head)))
