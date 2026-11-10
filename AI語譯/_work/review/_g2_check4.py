# -*- coding: utf-8 -*-
import io, json
rows = json.load(open(r"AI語譯/_work/review/_g2_re9_rows.json", encoding="utf-8"))
base = {(d["book"], d["chunk"], d["seg"]): d["current"].replace("\n", "") for d in rows}
for l in io.open(r"AI語譯/_work/review/fix_re9_g2.tsv", encoding="utf-8").read().split("\n"):
    if not l.strip():
        continue
    b, c, s, new = l.split("\t")
    old = base[(b, c, s)]
    if new == old:
        print("NOCHANGE", b, c, s)
    # find immediate repetition of len>=7 substrings
    L = 7
    for i in range(len(new) - 2 * L):
        if new[i:i+L] == new[i+L:i+2*L]:
            # ignore if already in old at same spot-ish
            frag = new[i:i+L]
            if old.count(frag) >= 2:
                continue
            print("REPEAT %s %s s%s: ...%s..." % (b, c, s, new[max(0, i-30):i+2*L+30]))
            break
