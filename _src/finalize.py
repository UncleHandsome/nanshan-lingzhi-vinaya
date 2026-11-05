
import os, glob, io, shutil
base = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
d = os.path.join(base, '白話')
old = os.path.join(d, '舊版')
os.makedirs(old, exist_ok=True)
for f in glob.glob(os.path.join(d, '*')):
    n = os.path.basename(f)
    if os.path.isdir(f):
        continue
    if f.endswith('.png'):
        os.remove(f); continue
    if '定本' not in n:
        shutil.move(f, os.path.join(old, n))
print(sorted(os.listdir(d)))
print(sorted(os.listdir(old)))

# README update
p = os.path.join(base, 'README.md')
s = io.open(p, encoding='utf-8').read()
start = s.find('## 六、白話語譯')
if start > 0:
    s = s[:start]
s = s.rstrip() + '''

---

## 六、白話語譯（白話／）

《行事鈔》卷一（序、標宗顯德篇、集僧通局篇）白話語譯，兩種版本：

| 檔案 | 說明 | 頁數 |
|:--|:--|--:|
| 行事鈔_白話對照本_卷一_定本.pdf | 每節先列原文（楷體、淺底），次列語譯 | 32 |
| 行事鈔_全白話本_卷一_定本.pdf | 只存語譯，供通讀 | 25 |

語譯依讀者指定之版本排印；初稿與修訂稿見「白話／舊版」。
'''
io.open(p, 'w', encoding='utf-8').write(s)
print('readme updated')
