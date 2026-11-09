import json, re

out = json.load(open("AI語譯/_work/review/_jb2.json", encoding="utf-8"))
jb = json.load(open("AI語譯/_work/review/_jb.json", encoding="utf-8"))

def norm(s):
    return s.replace("『", "「").replace("』", "」")

manual_idx = []
for x in out:
    if x["npair"] == 0:
        manual_idx.append(x["i"])
        continue
    if not all(a in x["cur"] or norm(a) in x["cur"] for a, b in x["pairs"]):
        manual_idx.append(x["i"])

print("manual rows", len(manual_idx))
with open("AI語譯/_work/review/_prob.txt", "w", encoding="utf-8") as f:
    for i in manual_idx:
        x = out[i]
        r = jb[i]
        f.write(f"[{i}] {x['chunk']} seg{x['seg']} cls={r['cls']}\nP:{r['problem']}\nS:{x['sug'] or '(空)'}\n\n")
