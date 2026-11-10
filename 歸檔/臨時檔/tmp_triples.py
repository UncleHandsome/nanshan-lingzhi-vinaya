# -*- coding: utf-8 -*-
import re, json

rows = json.load(open("tmp_rows.json", encoding="utf-8"))
n = len(rows)
END = "。！？；：」』〕）…"

def typ(r):
    return "鈔" if r["orig"].startswith("【鈔】") else ("記" if r["orig"].startswith("【記】") else "?")

out = []
for i in range(n - 2):
    a, b, c = rows[i], rows[i+1], rows[i+2]
    if typ(a) == "記" and typ(b) == "鈔" and typ(c) == "記":
        out.append((i, a["id"], b["id"], c["id"], a["orig"], b["orig"], c["orig"], a["trans"], c["trans"]))

print("triples", len(out))
with open("tmp_triples.txt", "w", encoding="utf-8") as f:
    for i, aid, bid, cid, ao, bo, co, at, ct in out:
        f.write(f"{aid} | {bid} | {cid}\n")
        f.write(f"  記末40: {ao[-40:]}\n")
        f.write(f"  鈔首40: {bo[:40]}\n")
        f.write(f"  後記首60: {co[3:63]}\n")
        f.write("---\n")

# also list all 記 paragraphs (any) whose ending lacks terminal punctuation
nopunct = []
for r in rows:
    if typ(r) == "記":
        if r["orig"] and r["orig"][-1] not in END:
            nopunct.append(r["id"])
print("記無標點結尾:", len(nopunct), nopunct[:50])
