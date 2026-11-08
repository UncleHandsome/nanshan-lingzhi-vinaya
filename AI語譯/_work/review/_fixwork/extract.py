# -*- coding: utf-8 -*-
import json, re, os

W = r"AI語譯/_work/review/_fixwork"
rows = [json.loads(l) for l in open(os.path.join(W, "zi.jsonl"), encoding="utf-8")]

OPEN = "「"; CLOSE = "」"

def balanced(s, start):
    """s[start] must be OPEN; return (inner, end_index_exclusive) or None."""
    if start >= len(s) or s[start] != OPEN:
        return None
    depth = 0
    i = start
    while i < len(s):
        c = s[i]
        if c == OPEN:
            depth += 1
        elif c == CLOSE:
            depth -= 1
            if depth == 0:
                return s[start+1:i], i+1
        i += 1
    return None

VERBS = ["修正為", "改譯為", "改為", "改作", "應作", "應改為"]

def parse_ops(sug):
    """Return list of (kind, a, b) ops where kind in {rep, del, append, prepend}."""
    ops = []
    i = 0
    while i < len(sug):
        # find next verb
        m = None
        for v in VERBS:
            j = sug.find(v, i)
            if j != -1:
                if m is None or j < m[0]:
                    m = (j, v)
        if m is None:
            break
    # above loop broken; redo linearly
    return ops

def find_ops(sug):
    res = []
    pos = 0
    while True:
        best = None
        for v in VERBS:
            j = sug.find(v, pos)
            if j != -1 and (best is None or j < best[0]):
                best = (j, v)
        if best is None:
            break
        j, v = best
        # B: quoted string right after verb (allow ：: ， spaces)
        k = j + len(v)
        while k < len(sug) and sug[k] in "：:﹕ ,，":
            k += 1
        b = None
        if k < len(sug) and sug[k] == OPEN:
            r = balanced(sug, k)
            if r:
                b, _ = r
        # A: scan backwards from j, skipping the verb chars; find last balanced 「…」 ending at/before j
        a = None
        # try: optional 將 before open quote; search backwards for a CLOSE at or before j
        end = j
        # trim trailing spaces
        while end > 0 and sug[end-1] == " ":
            end -= 1
        if end > 0 and sug[end-1] == CLOSE:
            # walk back to matching OPEN
            depth = 0
            q = end - 1
            while q >= 0:
                if sug[q] == CLOSE:
                    depth += 1
                elif sug[q] == OPEN:
                    depth -= 1
                    if depth == 0:
                        break
                q -= 1
            if q >= 0:
                a = sug[q+1:end-1]
        res.append((j, v, a, b))
        pos = j + len(v)
    return res

out = []
for r in rows:
    sug = r["suggestion"].strip()
    cur = r["current"]
    rec = dict(idx=r["idx"], gid=r["gid"], chunk=r["chunk"], seg=r["seg"],
               level=r["level"], cls=r["cls"], problem=r["problem"],
               suggestion=sug, current=cur, nops=0, mode="", a_ok=[], new=cur, note="")
    if not sug:
        rec["mode"] = "skip_nosugg"
        out.append(rec); continue
    if sug.startswith("將整段譯文替換") or "整段譯文替換" in sug:
        rec["mode"] = "manual_fullpara"
        out.append(rec); continue
    ops = find_ops(sug)
    rec["nops"] = len(ops)
    # classify each op
    good = []
    bad = []
    for (j, v, a, b) in ops:
        if a is None or b is None:
            bad.append((v, a, b)); continue
        c = cur.count(a)
        if c == 1:
            good.append((a, b))
        else:
            bad.append((v, a, b, c))
    rec["a_ok"] = [[a, b] for a, b in good]
    rec["bad"] = [[str(x) for x in t] for t in bad]
    netxt = cur
    for a, b in good:
        netxt = netxt.replace(a, b, 1)
    rec["auto_new"] = netxt
    if len(bad) == 0 and len(good) > 0:
        rec["mode"] = "auto"
        rec["new"] = netxt
    elif len(good) > 0:
        rec["mode"] = "manual_partial"
        rec["new"] = netxt
    else:
        rec["mode"] = "manual_other"
    out.append(rec)

with open(os.path.join(W, "parsed.jsonl"), "w", encoding="utf-8") as f:
    for rec in out:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

from collections import Counter
print(Counter(x["mode"] for x in out))
print("auto nops dist:", Counter(x["nops"] for x in out if x["mode"] == "auto"))
