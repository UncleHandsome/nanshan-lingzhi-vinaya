p = r"AI語譯\_work\review\report_re8.tsv"
with open(p, encoding="utf-8") as f:
    txt = f.read()
lines = txt.split("\n")
out=[]
for i in range(470, 486):
    l = lines[i-1]
    out.append(f"--- line {i} len={len(l)} nf={len(l.split(chr(9)))}")
    out.append(repr(l[:400]))
open(r"_re8g1_peek.txt","w",encoding="utf-8").write("\n".join(out))
print("done")
