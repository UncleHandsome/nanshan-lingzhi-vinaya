import io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
s = io.open(B + r'\會本材料_11-30\業疏重譯\ye_new.txt', encoding='utf-8-sig').read()
keys = sorted(set(re.findall(r'"(\d\d[a-z]_卷[^"]+)"', s)))
print(len(keys))
print(keys)
