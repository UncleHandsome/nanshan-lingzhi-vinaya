
# -*- coding: utf-8 -*-
import io, os, json
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RV = os.path.join(D,'AI語譯','review_low_all')
rows = {}
for f in sorted(os.listdir(RV)):
    if not f.endswith('.json'): continue
    book = f.split('__')[0]
    arr = json.load(io.open(os.path.join(RV,f), encoding='utf-8'))
    rows[book] = rows.get(book, 0) + len(arr)
lines = ['# 校對進度（review_low_all）', '',
         '校對意見共 %d 條。' % sum(rows.values()), '',
         '| 書 | 意見數 | 狀態 |', '|:--|--:|:--|']
done = {'05_拾毗尼義鈔': '已修約 34 條（首解、提舍尼、十一戒等系統性錯誤）',
        '04_比丘尼鈔': '已修 7 條，其餘待修'}
for b, n in sorted(rows.items(), key=lambda x: -x[1]):
    lines.append('| %s | %d | %s |' % (b, n, done.get(b, '待修')))
lines += ['', '## 修法', '人工逐條：讀原文→判斷→改譯文→驗段數。每輪約 3–5 條。', '']
io.open(os.path.join(D,'AI語譯','審校進度.md'),'w',encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines))
