# -*- coding: utf-8 -*-
"""YE-G03 補頭尾：擴充 raw 區間，頭段＋原六段＋尾段共 8 段。

- raw_start/raw_end 由原文漢字流重新定位，不用模糊比對。
- source = 擴充後的 raw 切片（漢字序列必須完全等於 h[a:b]）。
- 已被新 G03 完整覆蓋的舊單元移除（專案既定規則：G 段完整覆蓋即併入）。
- 其餘行原樣保留（逐行改寫，不重新序列化全檔）。
"""
import io
import json
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RAW = os.path.join(B, 'TXT', '03_四分律刪補隨機羯磨疏.txt')
JSONL = os.path.join(B, '定稿', 'yeshu.jsonl')

HEAD = '四分中，都無覆者，方與行法。若順教緣，犯竟無覆，即從求學。'
TAIL = ('牒釋中，初通示教意。「此」下，別釋兩篇不同之相：初明初篇盡露方開，'
        '文牒「都無覆者」，乃據臨懺同篇盡露，非謂從初始終無覆，古今兩義通塞可見。'
        '「僧」下，次明二篇隨懺皆得隱顯，即是覆露、罪夜離合：罪謂本犯，夜即覆日；'
        '離則各隨長短，合則以短從長，即知隨懺不必盡露。')
HEAD_TR = ('《四分律》中，只有完全沒有覆藏的人，才為他行學悔之法。'
           '若是隨順教法所說的因緣——犯戒之後始終沒有覆藏，就聽許他立即依從求學（受學悔法）。')
TAIL_TR = ('在「牒釋」這一部分中，開頭先總體顯示教法的意旨。從「此」字以下，'
           '才分別解釋兩篇（波羅夷篇與僧殘篇）情況不同的相狀：首先說明初篇必須完全發露才開許懺悔'
           '——疏文引牒「都無覆者」這句，是就臨懺時同篇的罪全都發露來說的，'
           '並不是說從最初到最後都毫無覆藏；古、今兩種解釋哪一種通達、哪一種滯塞，由此可見。'
           '接著「僧殘不爾」以下，其次說明二篇隨著懺悔，都可以有隱有顯，'
           '這就是「覆露」與「罪夜離合」：罪指本來的犯事，夜指覆藏的天數；'
           '分開，就各隨本身罪與覆的長短；合併，就是以短的就長的。'
           '由此可知，隨分懺悔，不必全部發露。')


def han(s):
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))


raw = io.open(RAW, encoding='utf-8').read()
h = ''
mp = []
for i, c in enumerate(raw):
    if '\u4e00' <= c <= '\u9fff':
        h += c
        mp.append(i)

lines = io.open(JSONL, encoding='utf-8', newline='').read().split('\r\n')
if lines and lines[-1] == '':
    lines.pop()
rows = [json.loads(x) for x in lines]
assert all(rows[i]['key'] != rows[i - 1]['key'] for i in range(1, len(rows)))

r = next(x for x in rows if x['key'] == 'YE-G03')
old = r['segments']

# 定位：頭段起點、尾段終點
a = h.find(han(HEAD), 287000)
assert a >= 0, 'head not found'
assert a == 287424, a                       # 舊 raw_start 287447 - 頭段 23 字
assert a + len(han(HEAD)) == r['raw_start'], (a, r['raw_start'])
b = h.find(han(TAIL), r['raw_end'])
assert b == r['raw_end'], (b, r['raw_end'])
e = b + len(han(TAIL))
assert e == 287845, e

# 原六段漢字序列必須等於舊區間
assert ''.join(han(s['source']) for s in old) == h[r['raw_start']:r['raw_end']]
# 頭尾漢字亦須與原文一致
assert han(HEAD) == h[a:r['raw_start']]
assert han(TAIL) == h[b:e]

src = raw[mp[a]:mp[e - 1] + 1].strip()
assert han(src) == h[a:e], 'source != raw slice'
assert src.startswith('四分中都無覆者') and src.endswith('即知隨懺不必盡露'), (src[:10], src[-10:])

segs = [{'label': '疏文', 'source': HEAD, 'translation': HEAD_TR, 'display_source': HEAD}]
segs += old
segs.append({'label': '記文', 'source': TAIL, 'translation': TAIL_TR, 'display_source': TAIL})

r['raw_start'], r['raw_end'] = a, e
r['source'] = src
r['display_source'] = '\n'.join(s['display_source'] for s in segs)
r['translation'] = '\n'.join('【%s】%s' % (s['label'], s['translation']) for s in segs)
r['segments'] = segs
r['vol'] = '卷四'
r['chunk'] = '卷四之四'

# G 段完整覆蓋的舊單元併入（只認 100% 被蓋住且漢字相同的）
drop = []
out = []
for line, x in zip(lines, rows):
    if x['key'] == 'YE-G03':
        out.append(json.dumps(x, ensure_ascii=False))
        continue
    xa, xb = x.get('raw_start', -1), x.get('raw_end', -1)
    if xa >= a and xb <= e and xb > xa:
        assert han(x.get('source', '')) == h[xa:xb], x['key']
        drop.append(x['key'])
        continue
    out.append(line)
assert drop == ['22a_卷四之五_0127', '22b_卷四之五_0001'], drop

io.open(JSONL, 'w', encoding='utf-8', newline='').write('\r\n'.join(out) + '\r\n')
print('raw_start', a, 'raw_end', e, 'source_han', len(han(src)),
      'segments', len(segs), 'rows', len(rows), '->', len(out), 'dropped', drop)
