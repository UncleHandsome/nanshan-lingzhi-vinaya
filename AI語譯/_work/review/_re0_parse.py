# -*- coding: utf-8 -*-
import re, io, json, os

SRC = r"校閱批次/new/已完成/re0/re0.txt"
OUT = r"AI語譯/_work/review/_re0"

os.makedirs(OUT, exist_ok=True)
txt = io.open(SRC, encoding="utf-8-sig").read()
lines = txt.split("\n")

items = []
cur = None
for ln in lines:
    if ln.startswith("### "):
        if cur:
            items.append(cur)
        cur = {"header": ln[4:].strip(), "body": []}
    elif cur is not None:
        cur["body"].append(ln)
if cur:
    items.append(cur)

entries = []
for it in items:
    h = it["header"]
    if not re.match(r"^【?\d{3}-\d{4}", h):
        continue  # 存疑 sections
    body = "\n".join(it["body"])
    # fields
    def get(label):
        m = re.search(r"^- %s：(.*)$" % label, body, re.M)
        return m.group(1).strip() if m else None
    # header forms: gid｜book/chunk#seg｜P?｜type   or  【gid】book/chunk#seg｜P?｜type
    m = re.match(r"^【?(\d{3}-\d{4})】?(.*)$", h)
    gid = m.group(1)
    rest = m.group(2).strip()
    rest = rest.lstrip("｜|")
    if rest.startswith("｜"):
        parts = rest.split("｜")
        loc = parts[0]
        prio = parts[1] if len(parts) > 1 else ""
        typ = parts[2] if len(parts) > 2 else ""
    else:
        # merged: book/chunk#seg｜P0｜type
        parts = rest.split("｜")
        loc = parts[0]
        prio = parts[1] if len(parts) > 1 else ""
        typ = parts[2] if len(parts) > 2 else ""
    mm = re.match(r"^(.+?)/(.+?)#(\d+)$", loc)
    book, chunk, seg = (mm.group(1), mm.group(2), int(mm.group(3))) if mm else (None, None, None)
    entries.append({
        "gid": gid, "book": book, "chunk": chunk, "seg": seg,
        "prio": prio, "type": typ,
        "orig": get("原文起首"),
        "problem": get("問題"),
        "basis": get("依據"),
        "suggestion": get("建議"),
        "conf": get("信心"),
        "raw_header": h,
    })

json.dump(entries, io.open(os.path.join(OUT, "entries.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("entries:", len(entries))
print("no-suggestion:", sum(1 for e in entries if not e["suggestion"]))
print("bad-loc:", [(e["gid"], e["raw_header"]) for e in entries if e["book"] is None])
from collections import Counter
key = [(e["gid"], e["book"], e["chunk"], e["seg"], e["prio"], e["type"]) for e in entries]
dups = {k: c for k, c in Counter(key).items() if c > 1}
print("dup keys:", len(dups))
print("unique keys:", len(set(key)))
print("books:", Counter(e["book"] for e in entries))
print("prio:", Counter(e["prio"] for e in entries))
print("types:", Counter(e["type"] for e in entries))

