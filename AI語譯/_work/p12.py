import re, os, sys, json, difflib, collections
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
uniq=json.load(open(r"AI語譯\_work\work2.json",encoding="utf-8"))
stat=collections.Counter()
for r in uniq:
    cur=r["cur"].strip(); sug=r["sug"].strip()
    if cur==sug: r["cls"]="SAME"
    else:
        sm=difflib.SequenceMatcher(None,cur,sug); r["ratio"]=round(sm.ratio(),4)
        ops=[o for o in sm.get_opcodes() if o[0]!='equal']; r["nops"]=len(ops)
        r["cls"]="NEAR" if sm.ratio()>=0.9 else ("MID" if sm.ratio()>=0.6 else "FAR")
    stat[r["cls"]]+=1
print(stat)
json.dump(uniq,open(r"AI語譯\_work\work2.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
for r in uniq:
    if r["cls"]!="SAME":
        print(f'{r["cls"]:<4} {r["base"]:<20} {r["book"]}/{r["chunk"]}#{r["found"]} ratio={r["ratio"]} nops={r["nops"]} cur={len(r["cur"])} sug={len(r["sug"])}')
