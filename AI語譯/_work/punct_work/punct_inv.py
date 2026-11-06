import json, os, collections
base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work"
src = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\03_四分律刪補隨機羯磨疏_句讀_v3.txt"
v3 = open(src, encoding="utf-8").read()
cnt = collections.Counter(c for c in v3 if not c.isalnum() and not ('\u4e00'<=c<='\u9fff'))
for c,n in cnt.most_common(60):
    print(repr(c), hex(ord(c)), n)
