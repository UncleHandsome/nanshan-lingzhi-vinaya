# -*- coding: utf-8 -*-
import io, json, os
import _z6_lib as L
rows=[json.loads(l) for l in io.open("_z7_log.jsonl",encoding="utf-8") if l.strip()]
K=len(rows); M=sum(r["segs"] for r in rows); X=sum(r["veto"] for r in rows); Y=sum(r["doubt"] for r in rows)
print("K=%d M=%d edits=%d yi=%d run=%d X=%d Y=%d"%(K,M,sum(r["edits"] for r in rows),sum(r["yi"] for r in rows),sum(r["run"] for r in rows),X,Y))
for c in ["11a_中四上","11b_中四上","11c_中四上"]:
    t,s=L.paras(c); cur=(len(t.split(s)), t.count("\n"))
    b=L.rd(os.path.join(L.BAKDIR,c+"_v.txt")); bak=(len(b.split(s)), b.count("\n"))
    print(c,"cur",cur,"bak",bak,"OK" if cur==bak else "MISMATCH")
