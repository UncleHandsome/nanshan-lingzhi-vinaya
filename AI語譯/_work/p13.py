import re, os, sys, json, difflib, collections
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
work=json.load(open(r"AI語譯\_work\work2.json",encoding="utf-8"))
sel=[r for r in work if r["cls"]!="SAME"]
sel.sort(key=lambda r:(r["book"],r["chunk"],r["found"]))
L=[]
for r in sel:
    L.append(f'=== {r["base"]} | {r["book"]}/{r["chunk"]}#{r["found"]} | {r["cls"]} ratio={r["ratio"]} nops={r["nops"]} | src={r["src"]}')
    L.append(f'[判斷] {r["judge"]}')
    if r["origs"]: L.append(f'[原文] {r["origs"][0][:400]}')
    a=r["cur"].strip(); b=r["sug"].strip()
    sm=difflib.SequenceMatcher(None,a,b)
    for tag,i1,i2,j1,j2 in sm.get_opcodes():
        if tag=="equal": continue
        pre=a[max(0,i1-30):i1]; post=a[i2:i2+30]
        L.append(f'  [{tag}] …{pre}【-{a[i1:i2]}-】【+{b[j1:j2]}+】{post}…')
    L.append("")
open(r"AI語譯\_work\review2.txt","w",encoding="utf-8").write("\n".join(L))
print("entries",len(sel),"chars",sum(len(x) for x in L))
