import json, difflib, re
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
cur={}
for x in d: cur[(x["chunk"],x["seg"])]=x["CUR"]
out=[]
bad=0
for line in open(r"AI語譯\_work\review\fix_re8_g1.tsv",encoding="utf-8"):
    line=line.rstrip("\n")
    f=line.split("\t")
    if len(f)!=4: bad+=1; print("BADFIELDS",len(f)); continue
    if "\t" in f[3]: bad+=1
    k=(f[1],f[2])
    out.append((k,f[3]))
print("lines",len(out),"bad",bad)
print("unique keys",len(set(k for k,_ in out)))
# diff summary
lines=[]
cnt=0
for k,new in out:
    old=cur[k]
    sm=difflib.SequenceMatcher(None, old, new, autojunk=False)
    ops=[op for op in sm.get_opcodes() if op[0]!="equal"]
    cnt+=len(ops)
    lines.append(f"### {k[0]} {k[1]}  ({len(old)}->{len(new)}, {len(ops)} op)")
    for tag,i1,i2,j1,j2 in ops:
        pre=old[max(0,i1-12):i1]
        lines.append(f"  - {pre}[{old[i1:i2]}]{old[i2:i2+8]}")
        lines.append(f"  + {pre}[{new[j1:j2]}]{new[j2:j2+8]}")
print("diff ops",cnt)
open(r"AI語譯\_work\review\_re8g1_diff.txt","w",encoding="utf-8").write("\n".join(lines))
# suspicious: new much shorter than old
for k,new in out:
    old=cur[k]
    if len(new) < len(old)-40 or len(new) > len(old)+400:
        print("LENCHANGE",k,len(old),len(new))
