import json, re

out = json.load(open("AI語譯/_work/review/_jb2.json", encoding="utf-8"))

def norm(s):
    return s.replace("『", "「").replace("』", "」")

print("current has 『:", sum(1 for x in out if "『" in x["cur"]))

def apply_pairs(x):
    """try normalized matching; return (newtext, applied_pairs, failed_pairs)"""
    t = x["cur"]
    applied, failed = [], []
    for a, b in x["pairs"]:
        na, nb = norm(a), norm(b)
        if na in t:
            t = t.replace(na, nb, 1)
            applied.append((a, b))
        elif a in t:
            t = t.replace(a, b, 1)
            applied.append((a, b))
        else:
            failed.append((a, b))
    return t, applied, failed

stat = {"all": 0, "some": 0, "none": 0}
left = []
for x in out:
    t, ap, fa = apply_pairs(x)
    if x["npair"] == 0:
        continue
    if ap and not fa:
        stat["all"] += 1
    elif ap and fa:
        stat["some"] += 1
    else:
        stat["none"] += 1
    if fa:
        left.append(x)

print(stat, "leftover rows with failed pairs", len(left))
json.dump(left, open("AI語譯/_work/review/_left.json", "w", encoding="utf-8"), ensure_ascii=False)

with open("AI語譯/_work/review/_left.txt", "w", encoding="utf-8") as f:
    for x in left:
        f.write(f"=== [{x['i']}] {x['chunk']} seg{x['seg']}\nSUG: {x['sug']}\n")
        for a, b in x["pairs"]:
            f.write(f"A: {a}\n  B: {b}\n")
        f.write("CUR: " + x["cur"] + "\n\n")
