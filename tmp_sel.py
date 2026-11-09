import json
data=json.load(open("AI語譯/_work/review/tmp_re8/groups.json",encoding="utf-8"))
sel=[30,33,35,39,40,47,51,52,53,55,61,62,63,64,67,70,72,25,28,19,45,59,60,23,24]
out=[]
for i in sel:
    k,gs=data[i]
    out.append(f"===== {i} | {k[0]} | {k[1]} | seg {k[2]} | len={len(gs[0]['current'])}")
    out.append(gs[0]["current"])
open("AI語譯/_work/review/tmp_re8/sel.txt","w",encoding="utf-8").write("\n".join(out))
print(sum(len(data[i][1][0]['current']) for i in sel))
