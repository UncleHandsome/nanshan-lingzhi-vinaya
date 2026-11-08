# -*- coding: utf-8 -*-
"""Final structural + quality verification of fix_new_g2.tsv."""
import json, re
from collections import Counter

ROWS = json.load(open(r"AI語譯\_work\review\_g2x\rows.json", encoding="utf-8"))
bykey = {}
for d in ROWS:
    bykey.setdefault((d["book"], d["chunk"], d["seg"]), d)

out = []
for ln in open(r"AI語譯\_work\review\fix_new_g2.tsv", encoding="utf-8").read().split("\n"):
    if ln:
        out.append(ln.split("\t"))

print("lines:", len(out), "| all 4 fields:", all(len(f) == 4 for f in out))
print("unique keys:", len({(f[0], f[1], f[2]) for f in out}))

# duplicated punctuation / doubled chars introduced by edits
for f in out:
    new = f[3]
    cur = bykey[(f[0], f[1], f[2])]["current"].replace("\r\n", "").replace("\n", "")
    for bad in ["。。", "，，", "、、", "；；", "：：", "（）", "「」", "『』", "  ", "，，"]:
        if new.count(bad) > cur.count(bad):
            print("!! doubled punct", bad, f[1], f[2])
    if not re.search(r"[。！？」』）]$", new):
        print("!! odd ending", f[1], f[2], repr(new[-12:]))

# how many changed lines still contain leftover classical markers typical of untranslated text
marks = ["云：", "故文云", "應作", "若爾", "已", "訖"]
print()
print("chunk counts:", Counter(f[1] for f in out))
print()
print("seg list:", [(f[1].split("_")[0], f[2]) for f in out])

# skipped rows: confirm the flagged sentence really is gone (report as evidence)
skipped_idx = [14, 28, 29, 30, 31, 32, 35, 47]
print()
keys = {(f[0], f[1], f[2]) for f in out}
for i in skipped_idx:
    d = ROWS[i - 1]
    key = (d["book"], d["chunk"], d["seg"])
    print("skip [%d] %s %s seg %s cls=%s | in output: %s" % (i, d["gid"], d["chunk"], d["seg"], d["cls"], key in keys))
