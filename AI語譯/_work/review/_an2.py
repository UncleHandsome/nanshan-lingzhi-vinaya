import csv, json, re
from collections import Counter

p = "AI語譯/_work/review/report_re5.tsv"
rows = []
with open(p, encoding="utf-8") as f:
    rd = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
    header = next(rd)
    for i, r in enumerate(rd):
        if len(r) != 10:
            continue
        rows.append(dict(zip(header, r)))

jb = [r for r in rows if r["book"] == "02_戒疏"]
out = []
for idx, r in enumerate(jb):
    s = r["suggestion"].strip()
    cur = r["current"]
    rec = {"i": idx, "seg": r["seg"], "chunk": r["chunk"], "len": len(cur)}
    # find all quoted pairs around 改為
    pairs = re.findall(r"「([^」]{1,200})」\s*(?:改為|改成|改譯為|修訂為|應改為)\s*「([^」]{1,400})」", s)
    rec["npair"] = len(pairs)
    rec["pairs_in"] = sum(1 for a, b in pairs if a in cur)
    rec["pairs"] = pairs
    rec["sug"] = s
    rec["cur"] = cur
    out.append(rec)

c = Counter((x["npair"], x["pairs_in"]) for x in out)
print("(npair, in) counts:", dict(c))
print("rows with >=1 pair present:", sum(1 for x in out if x["pairs_in"] > 0))
print("rows with pairs but none present:", sum(1 for x in out if x["npair"] > 0 and x["pairs_in"] == 0))
print("rows no pairs:", sum(1 for x in out if x["npair"] == 0))

json.dump(out, open("AI語譯/_work/review/_jb2.json", "w", encoding="utf-8"), ensure_ascii=False)

# write a readable report
with open("AI語譯/_work/review/_an2.txt", "w", encoding="utf-8") as f:
    for x in out:
        f.write(f"[{x['i']}] {x['seg']} npair={x['npair']} in={x['pairs_in']} len={x['len']}\n")
        f.write("  SUG: " + x["sug"] + "\n")
        for a, b in x["pairs"]:
            f.write(f"  A({a in x['cur']}): {a}\n  B: {b}\n")
        f.write("\n")
