import csv, json, collections, os, sys
p = r"AI語譯/_work/review/report_re8.tsv"
rows=[]
with open(p, encoding="utf-8", newline="") as f:
    r = csv.reader(f, delimiter="\t")
    header = next(r)
    for line in r:
        if not any(line): continue
        if len(line) < 10:
            print("SHORT", len(line), repr(line)[:100]); continue
        rows.append(dict(zip(header, line)))
print("total", len(rows), header)
print(collections.Counter(x["book"] for x in rows).most_common())
sel=[x for x in rows if x["book"] in ("資持記","02_戒疏","01_行事鈔")]
print("selected", len(sel))
grp=collections.OrderedDict()
for x in sel:
    k=(x["book"],x["chunk"],x["seg"])
    grp.setdefault(k,[]).append(x)
print("unique segs", len(grp))
print("empty suggestion rows", sum(1 for x in sel if not x["suggestion"].strip()))
print("newline in current", sum(1 for x in sel if "\n" in x["current"]))
os.makedirs("AI語譯/_work/review/tmp_re8", exist_ok=True)
data=[[list(k), [dict(gid=g["gid"],level=g["level"],cls=g["cls"],problem=g["problem"],suggestion=g["suggestion"],orig=g["orig"],current=g["current"]) for g in v]] for k,v in grp.items()]
with open("AI語譯/_work/review/tmp_re8/groups.json","w",encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
