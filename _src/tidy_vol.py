
import os, glob, shutil, io
base = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
d = os.path.join(base, '白話')
old = os.path.join(d, '舊版')
os.makedirs(old, exist_ok=True)
for f in glob.glob(os.path.join(d, '*.pdf')) + glob.glob(os.path.join(d, '*.docx')):
    n = os.path.basename(f)
    if '定本v2' in n:
        shutil.move(f, os.path.join(old, n))
p = os.path.join(base, 'README.md')
s = io.open(p, encoding='utf-8').read()
start = s.find('## 六、白話語譯')
if start > 0:
    s = s[:start]
s = s.rstrip() + '''

---

## 六、白話語譯（白話／）

《行事鈔》白話語譯，按上、中、下三卷分冊。目前完成上卷之序與第一、二篇，餘篇待續。

| 檔案 | 說明 | 頁數 |
|:--|:--|--:|
| 行事鈔_白話對照本_上卷.pdf | 每節先列原文（10.5pt 楷體、淺底），次列語譯 | 29 |
| 行事鈔_全白話本_上卷.pdf | 只存語譯 | 21 |

舊稿見「白話／舊版」；AI 語譯工作區見「AI語譯」。
'''
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
