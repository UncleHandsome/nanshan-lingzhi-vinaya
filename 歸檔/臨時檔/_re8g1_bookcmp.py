import json, difflib
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
book={}
for ch in set(x["chunk"] for x in d):
    book[ch]=[l for l in open(rf"AI語譯\out\03_業疏\{ch}.txt",encoding="utf-8").read().split("\n") if l.strip()]
out={}
for line in open(r"AI語譯\_work\review\fix_re8_g1.tsv",encoding="utf-8"):
    f=line.rstrip("\n").split("\t"); out[(f[1],f[2])]=f[3]
diffsegs=set()
for x in d:
    cur=x["CUR"].strip(); idx=int(x["seg"])-1
    ls=book[x["chunk"]]
    if not (0<=idx<len(ls) and ls[idx].strip()==cur):
        diffsegs.add((x["chunk"],x["seg"]))
print("diff segments:",len(diffsegs))
for k in sorted(diffsegs):
    ch,seg=k; ls=book[ch]; idx=int(seg)-1
    new=out.get(k)
    bk=ls[idx] if 0<=idx<len(ls) else "<OOR>"
    if new is None:
        print(k,"NO-OUTPUT; book==?", bk[:30]); continue
    if new==bk:
        print(k,"IDENTICAL-TO-BOOK")
    else:
        sm=difflib.SequenceMatcher(None,bk,new,autojunk=False)
        ops=[op for op in sm.get_opcodes() if op[0]!="equal"]
        s=[]
        for tag,i1,i2,j1,j2 in ops[:4]:
            s.append(f"book[{bk[i1:i2]}]->new[{new[j1:j2]}]")
        print(k,"DIFF:", " ".join(s)[:200])
