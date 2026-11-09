import csv, json, re, io, os

p = "AI語譯/_work/review/report_re5.tsv"
rows = []
with open(p, encoding="utf-8") as f:
    rd = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
    header = next(rd)
    for i, r in enumerate(rd):
        if len(r) != 10:
            print("BADLEN", i+2, len(r))
            continue
        rows.append(dict(zip(header, r)))

jb = [r for r in rows if r["book"] == "02_戒疏"]
print("total", len(rows), "02戒疏", len(jb))

# key uniqueness
from collections import Counter
c = Counter((r["chunk"], r["seg"]) for r in jb)
print("unique chunk+seg", len(c), "dups", [(k,v) for k,v in c.items() if v>1][:20])

nosug = [r for r in jb if not r["suggestion"].strip()]
print("nosug", len(nosug))
withsug = [r for r in jb if r["suggestion"].strip()]
print("withsug", len(withsug))

# classify suggestion patterns
pats = Counter()
for r in withsug:
    s = r["suggestion"]
    if "改為「" in s:
        pats["has_gaiwei"] += 1
    if re.search(r"整段|全段|建議改譯為|改譯為|建議譯為", s):
        pats["whole"] += 1
    if "「" in s:
        pats["has_quote"] += 1
print(pats)

# check presence of problem's first quote in current
def first_quote(s):
    m = re.search(r"「([^」]{2,30})」", s)
    return m.group(1) if m else None

miss = 0
for r in withsug:
    q = first_quote(r["problem"])
    r["_q"] = q
    r["_in"] = (q in r["current"]) if q else None
    if q and q not in r["current"]:
        miss += 1
print("first quote missing in current:", miss)

json.dump(jb, open("AI語譯/_work/review/_jb.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
