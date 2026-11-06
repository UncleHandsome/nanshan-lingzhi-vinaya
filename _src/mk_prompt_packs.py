# -*- coding: utf-8 -*-
"""產生篇11-30 可直接貼給 AI 的「鈔界」「切點」提示檔（資料內嵌）"""
import io, os, re, json, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
SECS = ex.sections(); ZI = ex.build_zi(SECS, ex.zsecs())
AM = json.load(io.open(os.path.join(B, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))
SKIP = re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇')
OUT = os.path.join(B, '會本材料_11-30')
os.makedirs(OUT, exist_ok=True)

HEAD = """# 會本標註：篇{p}　{name}

你是律學古籍校勘專家。下面給你《四分律行事鈔》（鈔）與《資持記》（記）的全文。
記是元照律師對鈔的逐句註釋，但段落切分不是按註釋對象切的，所以需要你判斷對應。

## 資料

### 鈔
{chao}

### 記
{ji}

## 任務
{task}

## 輸出格式
```json
{schema}
```

規則：
1. 只回 JSON，不要解釋。
2. `n` 必須是資料中出現的記號。
3. `c` 必須是資料中出現的鈔號。
"""

BOUNDS_TASK = """為每一條鈔（c=2 到最後）找出「它的註釋從哪一個記段開始」。

判斷方法：讀記文，找它開始解釋該鈔首句的科判語（「二就事明者」「初中」「次科」等）。
若鈔界落在兩記段之間，取其後那一段；不確定時保守取值，不要亂跳。"""

BOUNDS_SCHEMA = '{"bounds": [{"c": 2, "n": 5}, {"c": 3, "n": 13}, ...]}'

SPLITS_TASK = """找出「一段記文跨兩（或更多）條鈔」的記段，標出切點。

判斷方法：記文裡的科判語（「X中」「第X問」「次科」「三小中」）往往就是下一條鈔註釋的開頭。
若某記段前半在收上一鈔、後半開始解下一鈔，就要切。

marker 必須是該記段原文中「逐字出現」的短句（6–12 字），從科判語開始。
targets 是切開後各段對應的鈔號，必須從 base 起算連續遞增。"""

SPLITS_SCHEMA = '{"splits": [{"n": 16, "base": 4, "markers": ["大界中"], "targets": [4, 5]}]}'


def data_lines(p):
    idx = p - 1
    sec = SECS[idx]
    zi = ZI[idx]
    am = AM.get(str(idx), [])
    chao = [it[0] for it in sec['items'] if not SKIP.match(it[0].strip())]
    ch = '\n'.join('【鈔%02d】%s' % (i + 1, t) for i, t in enumerate(chao))
    ji = '\n'.join('【記%03d】(c=%d) %s' % (k + 1, int(am[k]) if k < len(am) else 0, zi[k][0])
                   for k in range(len(zi)))
    return ch, ji, len(chao), len(zi)


def write(p, kind):
    ch, ji, nc, nj = data_lines(p)
    name = SECS[p - 1]['name']
    if kind == 'bounds':
        task, schema = BOUNDS_TASK, BOUNDS_SCHEMA
    else:
        task, schema = SPLITS_TASK, SPLITS_SCHEMA
    txt = HEAD.format(p=p, name=name, chao=ch, ji=ji, task=task, schema=schema)
    fp = os.path.join(OUT, '篇%02d_%s.md' % (p, kind))
    io.open(fp, 'w', encoding='utf-8').write(txt)
    return fp, nc, nj


for p in range(11, 31):
    for kind in ('bounds', 'splits'):
        fp, nc, nj = write(p, kind)
    print('篇%02d %-8s 鈔%3d 記%4d' % (p, SECS[p - 1]['name'], nc, nj))
print('輸出', OUT)
