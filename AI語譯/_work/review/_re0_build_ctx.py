# -*- coding: utf-8 -*-
"""Parse re0.txt into entries (handles missing ### prefixes, dedupes exact dup blocks),
attach current paragraph text from AI語譯/out, emit a review dump."""
import re, io, json, os
from collections import Counter, OrderedDict

SRC = r"校閱批次/new/已完成/re0/re0.txt"
OUT = r"AI語譯/_work/review/_re0"
os.makedirs(OUT, exist_ok=True)

lines = io.open(SRC, encoding="utf-8-sig").read().split("\n")

HDR = re.compile(r"^\s*(?:###\s*)?【?(\d{3}-\d{4})】?\s*(.*)$")
ENTRY = re.compile(r"^\s*(?:###\s*)?【?(\d{3}-\d{4})】?\s*(.+?/\S+?#\d+)｜(P[012])｜(.+?)\s*$")

items = []
cur = None
for ln in lines:
    if ln.strip().startswith("### "):
        if cur: items.append(cur)
        cur = {"header": ln.strip()[4:].strip(), "body": []}
        continue
    if ENTRY.match(ln) and not ln.strip().startswith("- "):
        if cur: items.append(cur)
        cur = {"header": ln.strip(), "body": []}
        continue
    if cur is not None:
        cur["body"].append(ln)
if cur: items.append(cur)

entries = []
for it in items:
    h = it["header"]
    m = ENTRY.match(h)
    if not m:
        continue
    gid, loc, prio, typ = m.group(1), m.group(2).lstrip("｜|"), m.group(3), m.group(4)
    book, chunk, seg = re.match(r"^(.+?)/(.+?)#(\d+)$", loc).groups()
    body = "\n".join(it["body"])
    def get(label):
        mm = re.search(r"^\s*- %s：(.*)$" % label, body, re.M)
        return mm.group(1).strip() if mm else None
    e = {"gid": gid, "book": book, "chunk": chunk, "seg": int(seg), "prio": prio,
         "type": typ, "orig": get("原文起首"), "problem": get("問題"),
         "basis": get("依據"), "suggestion": get("建議"), "conf": get("信心"),
         "raw_header": h, "body_lines": len(it["body"])}
    entries.append(e)

# exact duplicate detection: same gid/seg/type/problem/suggestion
def key(e):
    return (e["gid"], e["seg"], e["type"], e["problem"], e["suggestion"])
seen = {}
uniq = []
dups = []
for e in entries:
    k = key(e)
    if k in seen:
        dups.append((seen[k], e))
    else:
        seen[k] = e
        uniq.append(e)

# load paragraphs
para_cache = {}
def paras(book, chunk):
    k = (book, chunk)
    if k not in para_cache:
        p = r"AI語譯/out/%s/%s.txt" % (book, chunk)
        if not os.path.exists(p):
            para_cache[k] = None
        else:
            txt = io.open(p, encoding="utf-8").read()
            para_cache[k] = [seg for seg in txt.split("\n") if seg.strip()]
    return para_cache[k]

missing_file = []
for e in uniq:
    ps = paras(e["book"], e["chunk"])
    if ps is None:
        e["current"] = None
        missing_file.append(e["gid"])
    elif e["seg"] <= len(ps):
        e["current"] = ps[e["seg"] - 1]
    else:
        e["current"] = None
        missing_file.append(e["gid"] + " seg>%d" % len(ps))

json.dump(uniq, io.open(os.path.join(OUT, "uniq.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump([{"dup_of": a["gid"] + "/" + str(a["seg"]), "gid": b["gid"], "seg": b["seg"],
            "type": b["type"]} for a, b in dups],
          io.open(os.path.join(OUT, "dups.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("parsed entries:", len(entries))
print("unique entries:", len(uniq))
print("exact duplicate blocks:", len(dups))
print("missing/短seg:", missing_file)
print("prio uniq:", Counter(e["prio"] for e in uniq))
print("books uniq:", Counter(e["book"] for e in uniq))
# suggestion pattern classes
cls = Counter()
for e in uniq:
    s = e["suggestion"] or ""
    if re.search(r"將「[^」]*」改為「", s): cls["將A改為B"] += 1
    elif re.search(r"「[^」]*」改為「", s): cls["A改為B"] += 1
    elif re.search(r"修正為「|改為「", s): cls["改為X"] += 1
    elif "刪" in s: cls["刪"] += 1
    else: cls["other"] += 1
print("pattern classes:", cls)
