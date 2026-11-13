import re, json, os, glob
root = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
def read(p):
    with open(p, encoding="utf-8") as f: return f.read()

# 行事鈔 分卷 05a paragraphs
t = read(os.path.join(root, "TXT_分卷", "01_行事鈔", "05a_卷中之一.txt"))
lines = t.splitlines()
paras = [l for l in lines if l.startswith("\u3000\u3000")]
print("05a 分卷 paragraphs:", len(paras))
print("05a 分卷 non-empty lines:", len([l for l in lines if l.strip()]))
# out 05a
o = read(os.path.join(root, "AI語譯", "out", "01_行事鈔", "05a_卷中之一.txt"))
oblocks = [b for b in re.split(r"\n\s*\n", o) if b.strip()]
print("05a out blocks:", len(oblocks))
for i,b in enumerate(oblocks[:6]): print(i, len(b), b[:30].replace("\n"," "))
