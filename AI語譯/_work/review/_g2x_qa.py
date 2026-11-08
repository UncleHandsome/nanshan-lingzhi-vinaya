# -*- coding: utf-8 -*-
"""QA for fix_new_g2.tsv: structure, verbatim-preservation, and readable diffs."""
import csv, json, re, sys, difflib

ROWS = json.load(open(r"AI語譯\_work\review\_g2x\rows.json", encoding="utf-8"))
bykey = {}
for d in ROWS:
    bykey.setdefault((d["book"], d["chunk"], d["seg"]), d)

raw = open(r"AI語譯\_work\review\fix_new_g2.tsv", "rb").read()
print("BOM:", raw[:3] == b"\xef\xbb\xbf", "| bytes:", len(raw), "| CRLF:", b"\r" in raw)
text = raw.decode("utf-8")
out = []
for ln in text.split("\n"):
    if ln == "":
        continue
    out.append(ln.split("\t"))
print("lines:", len(out))

bad = 0
diffs = []
for f in out:
    assert len(f) == 4, f[:2]
    book, chunk, seg, new = f
    assert book == "01_行事鈔", book
    key = (book, chunk, seg)
    assert key in bykey, key
    cur = bykey[key]["current"]
    if "\n" in new or "\t" in new:
        print("!! newline/tab in", key); bad += 1
    if new == cur:
        print("!! unchanged line", key); bad += 1
    if not new.strip():
        print("!! empty", key); bad += 1
    # bracket / quote balance check (relative to current)
    for pair in ["「」", "『』", "（）", "《》"]:
        a, b = pair[0], pair[1]
        if new.count(a) - new.count(b) != cur.count(a) - cur.count(b):
            print("!! imbalance", pair, key, cur.count(a), cur.count(b), new.count(a), new.count(b)); bad += 1
    sm = difflib.SequenceMatcher(None, cur, new)
    ops = [(tag, cur[i1:i2], new[j1:j2]) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal"]
    diffs.append((key, cur, new, ops, bykey[key]["gid"]))

print("flagged:", bad)
print()
for key, cur, new, ops, gid in diffs:
    print("-" * 90)
    print(f"[{gid}] {key[1]} seg {key[2]}   len {len(cur)} -> {len(new)}")
    for tag, o, n in ops:
        print(f"  - {o!r}")
        print(f"  + {n!r}")
