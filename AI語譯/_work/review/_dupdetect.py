# -*- coding: utf-8 -*-
import csv, re
P = r"AI語譯/_work/review/report_re9.tsv"
rows = {}
with open(P, encoding="utf-8", newline="") as f:
    r = csv.reader(f, delimiter="\t")
    header = next(r)
    for i, row in enumerate(r, start=2):
        if len(row) < 10: continue
        d = dict(zip(header, row))
        if d["book"] != "05_拾毗尼義鈔": continue
        d["_line"] = i
        rows[i] = d

def longest_dup(s):
    """find repeated substring >= 40 chars: check prefix repeats of halves"""
    n = len(s)
    best = None
    # try: does s have form P + Q + Q ... ? check for each candidate start
    for i in range(0, n//2):
        # find next occurrence of s[i:i+30]
        probe = s[i:i+30]
        if len(probe) < 30: break
        j = s.find(probe, i+30)
        if j != -1:
            # extend match
            k = 0
            while j+k < n and i+k < j and s[i+k] == s[j+k]:
                k += 1
            if best is None or k > best[2]:
                best = (i, j, k)
    return best

for ln in (245, 246, 248, 251, 247, 249, 250):
    d = rows[ln]
    s = d["current"]
    b = longest_dup(s)
    print("="*100)
    print("line", ln, "seg", d["seg"], "len", len(s), "parts", len(s.split("\n")))
    if b:
        i, j, k = b
        print(f"  longest repeat: start1={i} start2={j} len={k}")
        print("  TEXT:", s[i:i+min(k,120)])
        print("  ...tail of first:", s[i+k-60:i+k])
        print("  ctx after 2nd:", s[j+k:j+k+100])
        # positions in joined text (ignoring newlines)
        flat = s.replace("\n", "")
        print("  flat len", len(flat))
