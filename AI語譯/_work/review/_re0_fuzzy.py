# -*- coding: utf-8 -*-
"""Fuzzy presence check: is a suggestion's target text already present in CUR or another paragraph?"""
import re, io, json, os, difflib
OUT = r"AI語譯/_work/review/_re0"
ents = json.load(io.open(os.path.join(OUT, "uniq2.json"), encoding="utf-8"))

cache = {}
def paras(book, chunk):
    k = (book, chunk)
    if k not in cache:
        p = r"AI語譯/out/%s/%s.txt" % (book, chunk)
        cache[k] = [s for s in io.open(p, encoding="utf-8").read().split("\n") if s.strip()]
    return cache[k]

def lcs_ratio(new, cur):
    sm = difflib.SequenceMatcher(None, new, cur, autojunk=False)
    m = sm.find_longest_match(0, len(new), 0, len(cur))
    return m.size / max(1, len(new))

def q(s):
    return s if s else ""

rows = []
for e in ents:
    sug = e["suggestion"] or ""
    cur = e["current"] or ""
    # candidate target text(s)
    cands = []
    for m in re.finditer(r"(?:補譯|改譯為|修改為|改為|更正為|修正為|替換為|改譯)[：:]?「([^」]+)」", sug):
        cands.append(m.group(1))
    if not cands:
        qs = re.findall(r"「([^「」]{8,})」", sug)
        if qs:
            cands = [max(qs, key=len)]
    if not cands:
        continue
    tgt = max(cands, key=len)
    self_r = lcs_ratio(tgt, cur)
    best = (0, None)
    for i, para in enumerate(paras(e["book"], e["chunk"])):
        if i + 1 == e["seg"]:
            continue
        r = lcs_ratio(tgt, para)
        if r > best[0]:
            best = (r, i + 1)
    rows.append({"gid": e["gid"], "seg": e["seg"], "type": e["type"],
                 "self": round(self_r, 2), "other": round(best[0], 2), "other_seg": best[1],
                 "tgt": tgt[:60]})

rows.sort(key=lambda r: -r["self"])
lines = []
for r in rows:
    lines.append("%s seg=%-4d self=%.2f other=%.2f@%s  %s" % (r["gid"], r["seg"], r["self"], r["other"], r["other_seg"], r["tgt"]))
io.open(os.path.join(OUT, "fuzzy.txt"), "w", encoding="utf-8").write("\n".join(lines))
print("rows", len(rows))
