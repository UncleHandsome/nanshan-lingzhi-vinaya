import json, io
p = r"AI語譯/_work/review/fix_dir_g2.tsv"
lines = io.open(p, encoding="utf-8").read().split("\n")
lines = [l for l in lines if l != ""]
print("lines", len(lines))
bad=0
for i,l in enumerate(lines):
    f=l.split("\t")
    if len(f)!=4: print("BAD cols", i, len(f)); bad+=1
    if "\n" in l or "\r" in l: print("BAD nl", i); bad+=1
print("bad", bad)
print("dup keys:", len(lines)-len(set("\t".join(l.split("\t")[:3]) for l in lines)))
for l in lines[:3]:
    f=l.split("\t"); print(f[0], f[1], f[2], len(f[3]), f[3][:60])
