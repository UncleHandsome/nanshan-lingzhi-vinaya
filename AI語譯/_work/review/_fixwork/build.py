# -*- coding: utf-8 -*-
import json, os
from collections import Counter

W = r"AI語譯/_work/review/_fixwork"
rows = [json.loads(l) for l in open(os.path.join(W, "zi.jsonl"), encoding="utf-8")]

OPEN = "\u300c"; CLOSE = "\u300d"; DOPEN = "\u300e"; DCLOSE = "\u300f"

def norm_d(s):
    return s.replace(DOPEN, OPEN).replace(DCLOSE, CLOSE)

def variants(a):
    vs = [a]
    n = norm_d(a)
    if n != a:
        vs.append(n)
    # also try current-style: if a has 「」 but current may have none
    return vs

def balanced(s, start):
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

VERBS = ["修正為", "改譯為", "改為", "改作"]

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
        k = j + len(v)
        while k < len(sug) and sug[k] in "\uff1a: ,\u3001":
            k += 1
        b = None
        if k < len(sug) and sug[k] == OPEN:
            r = balanced(sug, k)
            if r:
                b = r[0]
        a = None
        end = j
        while end > 0 and sug[end-1] == " ":
            end -= 1
        if end > 0 and sug[end-1] == CLOSE:
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

def locate(cur, a):
    for av in variants(a):
        c = cur.count(av)
        if c == 1:
            return cur.find(av), av
        if c > 1:
            return None, None
    return None, None

recs = []
for r in rows:
    sug = r["suggestion"].strip()
    cur = r["current"]
    rec = dict(r)
    rec["nops"] = 0
    rec["ops"] = []
    rec["new"] = cur
    rec["mode"] = ""
    rec["note"] = ""
    if not sug:
        rec["mode"] = "skip_nosugg"
        recs.append(rec); continue
    ops = find_ops(sug)
    rec["nops"] = len(ops)
    parsed = []
    for (j, v, a, b) in ops:
        if a is None or b is None:
            parsed.append(dict(a=a, b=b, ok=False, why="unparsed"))
            continue
        pos, am = locate(cur, a)
        if pos is None:
            if norm_d(a) in cur:
                parsed.append(dict(a=a, b=b, ok=False, why="multi"))
            elif b and norm_d(b) in cur:
                parsed.append(dict(a=a, b=b, ok=False, why="applied", bfound=True))
            else:
                parsed.append(dict(a=a, b=b, ok=False, why="missing"))
        else:
            parsed.append(dict(a=a, b=norm_d(b), ok=True, pos=pos, am=am))
    rec["ops"] = parsed
    okops = [p for p in parsed if p["ok"]]
    if okops and len(okops) == len(parsed):
        new = cur
        for p in sorted(okops, key=lambda x: -x["pos"]):
            new = new[:p["pos"]] + p["b"] + new[p["pos"]+len(p["am"]):]
        rec["new"] = new
        rec["mode"] = "auto"
    elif okops:
        rec["mode"] = "manual_partial"
    elif parsed and all(p.get("why") == "applied" for p in parsed):
        rec["mode"] = "skip_applied"
    else:
        rec["mode"] = "manual"
    recs.append(rec)

with open(os.path.join(W, "parsed2.jsonl"), "w", encoding="utf-8") as f:
    for r in recs:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print(Counter(r["mode"] for r in recs))
print("auto ops:", Counter(r["nops"] for r in recs if r["mode"] == "auto"))
print("manual idxs:", [r["idx"] for r in recs if r["mode"].startswith("manual")])
print("skip_applied idxs:", [r["idx"] for r in recs if r["mode"] == "skip_applied"])
