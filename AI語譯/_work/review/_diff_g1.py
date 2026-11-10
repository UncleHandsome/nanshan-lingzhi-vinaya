# -*- coding: utf-8 -*-
import sys, difflib
sys.path.insert(0, r"AI語譯/_work/review")
from _build3_g1 import main

out, stats = main()
lines = []
for key, txt, base, per in out:
    b = base.rstrip("\n").replace("\n", "")
    if txt == b: continue
    lines.append("="*100)
    lines.append(f"### {key[1]} seg={key[2]}  rows={[p['line'] for p in per]}")
    sm = difflib.SequenceMatcher(None, b, txt)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal": continue
        pre = b[max(0,i1-25):i1]
        post = b[i2:i2+25]
        lines.append(f"  [{tag}] …{pre}[[{b[i1:i2]}]]{post}…")
        lines.append(f"        -> …{pre}[[{txt[j1:j2]}]]{post}…")
open(r"AI語譯/_work/review/_diff_g1.txt","w",encoding="utf-8").write("\n".join(lines))
print("diff lines:", len(lines))
