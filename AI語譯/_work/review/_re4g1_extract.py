import json, re, io, os
p = r"AI語譯\_work\review\report_re4.tsv"
rows = []
with io.open(p, encoding="utf-8") as f:
    lines = f.read().split("\n")
header = lines[0]
for ln in lines[1:]:
    if not ln.strip():
        continue
    f = ln.split("\t")
    if len(f) != 11:
        print("BAD", len(f), ln[:80]); continue
    d = dict(zip(["gid","book","chunk","seg","level","cls","problem","suggestion","orig","tr","current"], f))
    if d["book"] != "02_戒疏":
        continue
    rows.append(d)
print("rows", len(rows))
os.makedirs(r"AI語譯\_work\review\_re4g1", exist_ok=True)
json.dump(rows, open(r"AI語譯\_work\review\_re4g1\rows.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
# pattern analysis of suggestions
pat_simple = 0; pat_other = []
for r in rows:
    s = r["suggestion"]
    m = re.match(r"^將「(.+?)」改為「(.+?)」", s)
    if not m:
        m2 = re.search(r"「(.+?)」改為「(.+?)」", s)
    if m:
        pat_simple += 1
    else:
        pat_other.append((r["gid"], r["chunk"], r["seg"], r["level"], r["cls"], s[:60]))
print("simple 將X改為Y:", pat_simple, "other:", len(pat_other))
for x in pat_other:
    print("  ", x)
