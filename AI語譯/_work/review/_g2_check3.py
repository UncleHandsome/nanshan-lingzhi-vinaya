# -*- coding: utf-8 -*-
import io, json, re
rows = json.load(open(r"AI語譯/_work/review/_g2_re9_rows.json", encoding="utf-8"))
base = {(d["book"], d["chunk"], d["seg"]): d["current"].replace("\n", "") for d in rows}
bad = ["。。", "，，", "；；", "、、", "：：", "））", "〕〕", "」。。", "，，"]
for l in io.open(r"AI語譯/_work/review/fix_re9_g2.tsv", encoding="utf-8").read().split("\n"):
    if not l.strip():
        continue
    book, chunk, seg, new = l.split("\t")
    old = base[(book, chunk, seg)]
    for b in bad:
        n_new = new.count(b)
        n_old = old.count(b)
        if n_new > n_old:
            i = new.find(b)
            print("%s %s s%s  %r old%d new%d : ...%s..." % (book, chunk, seg, b, n_old, n_new, new[max(0, i-40):i+40]))
    # empty-ish
    if len(new) < 3:
        print("SHORT", book, chunk, seg, repr(new))
