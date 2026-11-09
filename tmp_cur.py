import json
data=json.load(open("AI語譯/_work/review/tmp_re8/groups.json",encoding="utf-8"))
out=[]
for i,(k,gs) in enumerate(data):
    out.append(f"===== {i} | {k[0]} | {k[1]} | seg {k[2]} | len={len(gs[0]['current'])}")
    out.append(gs[0]["current"])
open("AI語譯/_work/review/tmp_re8/currents.txt","w",encoding="utf-8").write("\n".join(out))
# find newline case
for i,(k,gs) in enumerate(data):
    for g in gs:
        if "\n" in g["current"]:
            print("NEWLINE", i, k, repr(g["current"][:200]))
            j=g["current"].index("\n"); print(repr(g["current"][j-80:j+80]))
