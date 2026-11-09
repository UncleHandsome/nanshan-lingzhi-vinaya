import json
data=json.load(open("AI語譯/_work/review/tmp_re8/groups.json",encoding="utf-8"))
out=[]
for i,(k,gs) in enumerate(data):
    out.append(f"### {i} | {k[0]} | {k[1]} | seg {k[2]} | rows={len(gs)}")
    for g in gs:
        out.append(f"- [{g['gid']} {g['level']} {g['cls']}] P: {g['problem']}")
        out.append(f"  S: {g['suggestion']}")
open("AI語譯/_work/review/tmp_re8/list.txt","w",encoding="utf-8").write("\n".join(out))
print(len(out))
