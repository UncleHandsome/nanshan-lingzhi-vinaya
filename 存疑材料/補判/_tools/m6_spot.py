import os
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
def seg(path, n):
    t = open(path, encoding="utf-8-sig", newline="").read()
    ls = [l for l in t.split("\n") if l.strip()]
    return ls[n-1].rstrip("\r")
print(seg(os.path.join(ROOT, "AI語譯/out/03_業疏/22b_卷四之五.txt"), 89))
print()
print(seg(os.path.join(ROOT, "AI語譯/out/資持記/02f_上一下.txt"), 48))
print()
print(seg(os.path.join(ROOT, "AI語譯/out/03_業疏/00_卷首.txt"), 1)[:200])
