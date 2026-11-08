# -*- coding: utf-8 -*-
"""Context view: for each output line, show each edit spanning ~30 chars of context."""
import json, difflib

ROWS = json.load(open(r"AI語譯\_work\review\_g2x\rows.json", encoding="utf-8"))
bykey = {}
for d in ROWS:
    bykey.setdefault((d["book"], d["chunk"], d["seg"]), d)

out = []
for ln in open(r"AI語譯\_work\review\fix_new_g2.tsv", encoding="utf-8").read().split("\n"):
    if ln:
        out.append(ln.split("\t"))

buf = []
for book, chunk, seg, new in out:
    d = bykey[(book, chunk, seg)]
    cur = d["current"].replace("\r\n", "").replace("\n", "")
    sm = difflib.SequenceMatcher(None, cur, new)
    buf.append("=" * 100)
    buf.append(f"[{d['gid']}] {chunk} seg {seg}  ({len(cur)} -> {len(new)} chars)  cls={d['cls']}")
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        buf.append("- ..." + cur[max(0, i1 - 30):i1] + "【" + cur[i1:i2] + "】" + cur[i2:i2 + 30] + "...")
        buf.append("+ ..." + new[max(0, j1 - 30):j1] + "〖" + new[j1:j2] + "〗" + new[j2:j2 + 30] + "...")
    buf.append("")

open(r"AI語譯\_work\review\_g2x\ctx.txt", "w", encoding="utf-8").write("\n".join(buf))
print("ctx rows:", len(out), "| lines:", len(buf))
