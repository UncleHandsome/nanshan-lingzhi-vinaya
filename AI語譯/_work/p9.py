import re, os, sys, json, difflib, collections
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
work=json.load(open(r"AI語譯\_work\work.json",encoding="utf-8"))
blocks=json.load(open(r"AI語譯\_work\blocks.json",encoding="utf-8"))
bk=collections.defaultdict(list)
for b in blocks: bk[b["key"]].append(b)
def hunks(a,b,ctx=45):
    sm=difflib.SequenceMatcher(None,a,b); out=[]
    for tag,i1,i2,j1,j2 in sm.get_opcodes():
        if tag=="equal": continue
        pre=a[max(0,i1-ctx):i1]; post=a[i2:i2+ctx]
        out.append((tag,pre,a[i1:i2],b[j1:j2],post))
    return out
sel=[r for r in work if r["cls"]!="SAME"]
sel.sort(key=lambda r:(r["book"],r["chunk"],r["para"]))
lines=[]
for r in sel:
    lines.append(f'=== {r["base"]} | {r["book"]}/{r["chunk"]}#{r["para"]} | {r["cls"]} ratio={r.get("ratio")} | src={r["src"]} key={r["key"]} alias={r.get("alias")}')
    lines.append(f'[判斷] {r["judge"]}')
    for b in bk[r["base"]]:
        if b["orig"]: lines.append(f'[原文] {b["orig"]}')
    lines.append(f'[現行] {r["cur"]}')
    lines.append(f'[建議] {r["sug"]}')
    for tag,pre,old,new,post in hunks(r["cur"],r["sug"]):
        lines.append(f'  <{tag}> …{pre}〔-{old}-〕〔+{new}+〕{post}…')
    lines.append("")
open(r"AI語譯\_work\review_detail.txt","w",encoding="utf-8").write("\n".join(lines))
print("entries",len(sel),"chars",sum(len(x) for x in lines))
