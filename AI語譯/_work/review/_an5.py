import json, re

out = json.load(open("AI語譯/_work/review/_jb2.json", encoding="utf-8"))

def norm(s):
    return s.replace("『", "「").replace("』", "」")

def apply_pairs(x, textexact=True):
    t = x["cur"]
    applied, failed, modes = [], [], []
    for a, b in x["pairs"]:
        if a in t:
            t = t.replace(a, b, 1); applied.append((a, b)); modes.append("exact")
        elif norm(a) in t:
            t = t.replace(norm(a), norm(b), 1); applied.append((a, b)); modes.append("norm")
        else:
            failed.append((a, b)); modes.append("fail")
    return t, applied, failed, modes

cnt = {"exact": 0, "norm": 0, "fail": 0}
rows_info = []
for x in out:
    if x["npair"] == 0:
        continue
    t, ap, fa, modes = apply_pairs(x)
    for m in modes:
        cnt[m] += 1
    if fa:
        rows_info.append(x)
print(cnt, "rows failed", len(rows_info))

# ambiguous: A exact-matchable but also norm-matchable at a different place
amb = []
for x in out:
    for a, b in x["pairs"]:
        if "『" in a:
            if a in x["cur"] and norm(a) in x["cur"]:
                amb.append(x["i"])
print("rows with both exact and norm match for a 『』 pair:", sorted(set(amb)))

json.dump(rows_info, open("AI語譯/_work/review/_left.json", "w", encoding="utf-8"), ensure_ascii=False)
with open("AI語譯/_work/review/_left.txt", "w", encoding="utf-8") as f:
    for x in rows_info:
        f.write(f"=== [{x['i']}] {x['chunk']} seg{x['seg']}\nSUG: {x['sug']}\n")
        for a, b in x["pairs"]:
            f.write(f"A: {a}\n  B: {b}\n")
        f.write("CUR: " + x["cur"] + "\n\n")
