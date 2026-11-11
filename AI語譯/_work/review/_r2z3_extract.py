import re, os, json, sys
base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
mdir = os.path.join(base, "校閱_10K")
odir = os.path.join(base, "AI語譯", "out", "資持記")

# parse materials 895,908,909,911,913,914,915,920,922-925
files = [895]+list(range(908,910))+[911]+list(range(913,916))+[920]+list(range(922,926))
segs = {}
order = []
for n in files:
    p = os.path.join(mdir, f"校閱_{n:03d}.txt")
    txt = open(p, encoding="utf-8").read()
    # body after 材料開始
    body = txt.split("# 材料開始",1)[1]
    blocks = re.split(r"\n(?=【\d{3}-\d{4}】)", body)
    for b in blocks:
        m = re.match(r"【(\d{3})-(\d{4})】(資持記/[^#\s]+)#(\d+)", b)
        if not m: continue
        label = m.group(0)
        om = re.search(r"【原文】(.*?)(?=\n【譯文】)", b, re.S)
        tm = re.search(r"【譯文】(.*?)(?=\n\n【|\Z)", b, re.S)
        orig = om.group(1).strip() if om else ""
        trans = tm.group(1).strip() if tm else ""
        chunk = m.group(3).split("/",1)[1]; seg = int(m.group(4))
        if chunk not in ("01c_上一上","01d_上一上","01e_上一上","01f_上一上","02a_上一下"): continue
        segs[(chunk,seg)] = dict(label=label, resp=n, orig=orig, trans=trans)
        order.append((chunk,seg))

# load out paragraphs
outs = {}
for chunk in ["01c_上一上","01d_上一上","01e_上一上","01f_上一上","02a_上一下"]:
    p = os.path.join(odir, chunk+".txt")
    raw = open(p, encoding="utf-8").read()
    paras = [x for x in raw.split("\n") if x.strip()]
    outs[chunk] = dict(raw=raw, paras=paras)

rows = []
for chunk,seg in order:
    d = segs[(chunk,seg)]
    cur = outs[chunk]["paras"][seg-1]
    rows.append(dict(chunk=chunk, seg=seg, label=d["label"], resp=d["resp"], orig=d["orig"],
                     mat=d["trans"], cur=cur, same=(cur==d["trans"])))

# report counts and mismatches
from collections import Counter
c = Counter((r["chunk"]) for r in rows)
print("segments per chunk:", dict(c), "total", len(rows))
mm = [r for r in rows if not r["same"]]
print("mismatch:", len(mm))
for r in mm:
    print("---", r["label"], "matlen", len(r["mat"]), "curlen", len(r["cur"]))
print("paragraph counts:", {k: len(v["paras"]) for k,v in outs.items()})
json.dump(rows, open(os.path.join(base,"AI語譯","_work","review","_r2z3_rows.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved")
