
import os, glob, io
base = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
d = os.path.join(base, '白話')
for f in glob.glob(os.path.join(d, '*.png')):
    os.remove(f)
p = os.path.join(base, 'README.md')
s = io.open(p, encoding='utf-8').read()
start = s.find('## 六、白話語譯')
if start > 0:
    s = s[:start]
s = s.rstrip() + '''

---

## 六、白話語譯（白話／）

《行事鈔》全書白話語譯，分上、中、下三卷，各有對照本與全白話本。

| 冊 | 對照本 | 頁數 | 全白話本 | 頁數 |
|:--|:--|--:|:--|--:|
| 上卷 | 行事鈔_白話對照本_上卷.pdf | 181 | 行事鈔_全白話本_上卷.pdf | 124 |
| 中卷 | 行事鈔_白話對照本_中卷.pdf | 248 | 行事鈔_全白話本_中卷.pdf | 173 |
| 下卷 | 行事鈔_白話對照本_下卷.pdf | 221 | 行事鈔_全白話本_下卷.pdf | 152 |

- 語譯：Gemini 3.8 Flash（thinking high）分批產出，經四輪校讀修正；仍有零星待修處。
- 排版：原文 10.5pt 楷體淺底，譯文 12pt，行距 1.25，A4。
- 工作檔與各輪 review 紀錄在「AI語譯」。
'''
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
