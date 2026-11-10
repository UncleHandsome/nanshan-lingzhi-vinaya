import csv, json, re
p = r"AI語譯/_work/review/report_parts.tsv"
rows=[]
with open(p, encoding="utf-8", newline="") as f:
    r = csv.DictReader(f, delimiter="\t")
    for row in r:
        if row["book"]=="資持記":
            rows.append(row)
print("sel:", len(rows))
# sanity: no embedded issues
for i,x in enumerate(rows):
    for k in ("current","tr","problem","suggestion"):
        if "\n" in x[k] or "\r" in x[k]:
            print("NEWLINE in", i, k)
# triage
qre = re.compile(r"「([^」]*)」")
out=[]
for i,x in enumerate(rows):
    qs = qre.findall(x["problem"])
    qs2 = qre.findall(x["suggestion"])
    hit = [q for q in qs if q and q in x["current"]]
    miss = [q for q in qs if q and q not in x["current"]]
    out.append(dict(idx=i, gid=x["gid"], chunk=x["chunk"], seg=x["seg"], level=x["level"], cls=x["cls"],
                    same=(x["tr"]==x["current"]), qs=qs, hit=hit, miss=miss, sugqs=qs2,
                    problem=x["problem"], suggestion=x["suggestion"], current=x["current"], tr=x["tr"], orig=x["orig"], conf=x["conf"], basis=x["basis"]))
json.dump(out, open("_parts_rows.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
from collections import Counter
print("same & all-hit:", sum(1 for r in out if r["same"] and r["hit"] and not r["miss"]))
print("same & partial:", sum(1 for r in out if r["same"] and r["hit"] and r["miss"]))
print("same & no-hit:", sum(1 for r in out if r["same"] and not r["hit"] and r["miss"]))
print("same & no-quotes:", sum(1 for r in out if r["same"] and not r["qs"]))
print("diff (already applied?) :", sum(1 for r in out if not r["same"]))
print("diff & some hit:", sum(1 for r in out if not r["same"] and r["hit"]))
print("diff & no hit:", sum(1 for r in out if not r["same"] and not r["hit"]))
print("same & no-hit & no-quotes:", sum(1 for r in out if r["same"] and not r["qs"]))
