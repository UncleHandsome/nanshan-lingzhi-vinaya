
# -*- coding: utf-8 -*-
import io, os, json
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RV = os.path.join(D,'AI語譯','review_low_all')
rows = {}
for f in sorted(os.listdir(RV)):
    if not f.endswith('.json'): continue
    b = f.split('__')[0]
    rows[b] = rows.get(b, 0) + len(json.load(io.open(os.path.join(RV,f), encoding='utf-8')))
lines = ['# 校對進度', '',
 '## 已處理', '',
 '| 項目 | 條數 | 說明 |', '|:--|--:|:--|',
 '| 尼義鈔系統性錯誤 | 34 | 首解→智首律師、提舍尼→波逸提、十一戒→十戒 |',
 '| 尼鈔 03b 塊 | 10 | 主語、典故、叉手禮、衍字校記 |',
 '| 規則式明確改寫 | 20 | 「A改為B」型意見 |',
 '| 資持記 02e 漏譯 | 15 | 整句文言換白話 |',
 '| 全書漏譯掃蕩 | 51 | 行事鈔 26、資持記 24、戒疏 1 |',
 '| 「譯為「」」殘留清理 | 131 檔 | 全書批次 |',
 '| 標籤統一 | 52 處 | 【疏文譯文】→【疏文】 |',
 '', '## 待處理（誤譯／術語類，需逐段改寫）', '',
 '| 書 | 意見數 |', '|:--|--:|']
for b, n in sorted(rows.items(), key=lambda x: -x[1]):
    lines.append('| %s | %d |' % (b, n))
lines += ['', '## 方法', '一塊一輪：讀完該塊意見→整段改寫受影響段落→重建該書 PDF。', '']
io.open(os.path.join(D,'AI語譯','審校進度.md'),'w',encoding='utf-8').write('\n'.join(lines))
print('written')
