
import io, os, glob
base = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
for f in glob.glob(os.path.join(base, '白話', '*.png')):
    os.remove(f)
for f in glob.glob(os.path.join(base, '_src', 'find3.py')):
    os.remove(f)

p = os.path.join(base, 'README.md')
s = io.open(p, encoding='utf-8').read()
add = '''

---

## 六、白話語譯（白話／）

《行事鈔》白話語譯，分兩種版本，同一內容、同一分段：

| 檔案 | 說明 |
|:--|:--|
| 行事鈔_白話對照本_卷一.pdf | 逐段對照：先列原文（楷體、淺底），次列語譯 |
| 行事鈔_全白話本_卷一.pdf | 只存語譯，供通讀 |

目前進度：**序、標宗顯德篇第一、集僧通局篇第二**（全書三十篇，已完成三篇）。
譯文為初稿，供理解文義之用；引用、講說請覆核原文。其餘各篇待續。
'''
if '白話語譯' not in s:
    s = s.rstrip() + add
    io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
