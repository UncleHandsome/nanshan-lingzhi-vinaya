# -*- coding: utf-8 -*-
import csv, re, json
from collections import OrderedDict, Counter

P = r"AI語譯/_work/review/report_re9.tsv"
rows = []
with open(P, encoding="utf-8", newline="") as f:
    r = csv.reader(f, delimiter="\t")
    header = next(r)
    for i, row in enumerate(r, start=2):
        if len(row) < 10: continue
        d = dict(zip(header, row))
        if d["book"] != "05_拾毗尼義鈔": continue
        d["_line"] = i
        rows.append(d)

OPEN, CLOSE = "「", "」"
def balanced_quotes(s):
    """return list of (start,end_exclusive,inner) for outermost 「」 groups"""
    out = []
    i = 0
    n = len(s)
    while i < n:
        if s[i] == OPEN:
            depth = 1
            j = i + 1
            while j < n and depth > 0:
                if s[j] == OPEN: depth += 1
                elif s[j] == CLOSE: depth -= 1
                j += 1
            if depth == 0:
                out.append((i, j, s[i+1:j-1]))
                i = j
                continue
            else:
                break
        i += 1
    return out

REPL_VERBS = ["改為", "修正為", "改作", "應改為", "宜改為", "訂正為", "更正為"]
def parse_ops(sug):
    """return list of dicts: op in {replace, insert_after, delete}"""
    qs = balanced_quotes(sug)
    ops = []
    for k in range(len(qs) - 1):
        e1, i2 = qs[k][1], qs[k+1][0]
        sep = sug[e1:i2]
        verb = None
        for v in REPL_VERBS:
            if v in sep:
                verb = v
                break
        if verb and len(sep) <= 40:
            ops.append({"op": "replace", "a": qs[k][2], "b": qs[k+1][2]})
    # insert_after: 在「X」後...
    for m in re.finditer(r"在「", sug):
        pass
    for k in range(len(qs) - 1):
        e1, i2 = qs[k][1], qs[k+1][0]
        sep = sug[e1:i2]
        if "後" in sep and ("補" in sep or "增" in sep) and "改為" not in sep:
            ops.append({"op": "insert_after", "a": qs[k][2], "b": qs[k+1][2]})
    # delete: 刪除「X」 / 刪去「X」
    for q in qs:
        # find preceding 15 chars
        st = q[0]
        pre = sug[max(0, st-12):st]
        if "刪除" in pre or "刪去" in pre:
            ops.append({"op": "delete", "a": q[2], "b": ""})
    # dedupe
    return ops

res = []
for d in rows:
    sug = d["suggestion"].strip()
    cur = d["current"]
    if not sug:
        d["_cls"] = "EMPTY_SUG"
    else:
        ops = parse_ops(sug)
        if not ops:
            d["_cls"] = "NOPAT"
        else:
            d["_ops"] = ops
            miss = [o for o in ops if o["a"] not in cur]
            d["_cls"] = "OK" if not miss else "MISS"
    res.append(d)

print(Counter(d["_cls"] for d in res))
for c in ["NOPAT", "MISS"]:
    print(f"\n### {c} ###")
    for d in res:
        if d["_cls"] == c:
            print(f"line={d['_line']} {d['chunk']} seg={d['seg']} | SUG: {d['suggestion'][:160]}")
json.dump([{k:v for k,v in d.items() if not k.startswith('_')} for d in res], open(r"AI語譯/_work/review/_rows_g1.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
