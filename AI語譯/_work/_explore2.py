import re, os, json
root = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
def read(p):
    with open(p, encoding="utf-8") as f: return f.read()
t = read(os.path.join(root,"TXT_分卷","01_行事鈔","05a_卷中之一.txt"))
lines = t.splitlines()
out=[]
for i,l in enumerate(lines):
    s=l.strip()
    if not s: continue
    out.append(f"SRC {i+1:4d} {'P' if l.startswith('　　') else 'H'} len={len(s):4d} :: {s[:40]}")
o = read(os.path.join(root,"AI語譯","out","01_行事鈔","05a_卷中之一.txt"))
blocks=[b.strip() for b in re.split(r"\n\s*\n", o) if b.strip()]
for i,b in enumerate(blocks):
    out.append(f"OUT {i+1:4d} len={len(b):4d} :: {b[:40].replace(chr(10),' ')}")
open(os.path.join(root,"AI語譯","_work","_cmp05a.txt"),"w",encoding="utf-8").write("\n".join(out))
print("done", len(out))
