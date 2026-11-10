# -*- coding: utf-8 -*-
import json, io, os, re, sys, difflib
sys.path.insert(0, r"AI語譯/_work/review")
from _re0_decisions import D

OUT = r"AI語譯/_work/review/_re0"
ents = json.load(io.open(os.path.join(OUT, "uniq2.json"), encoding="utf-8"))

cache = {}
def paras(book, chunk):
    k = (book, chunk)
    if k not in cache:
        p = r"AI語譯/out/%s/%s.txt" % (book, chunk)
        cache[k] = [s for s in io.open(p, encoding="utf-8").read().split("\n") if s.strip()]
    return cache[k]

def apply_op(text, op, gid):
    kind = op[0]
    if kind == "apply":
        old, new = op[1], op[2]
        n = text.count(old)
        if len(op) > 3:
            idx = op[3]
            if n <= idx:
                return None, "OLD count=%d idx=%d for %r" % (n, idx, old[:60])
            pos = -1
            for _ in range(idx + 1):
                pos = text.find(old, pos + 1)
            return text[:pos] + new + text[pos + len(old):], None
        if n != 1:
            return None, "OLD count=%d for %r" % (n, old[:60])
        return text.replace(old, new), None
    if kind == "append":
        add = op[1]
        return text + add, None
    if kind == "rebuild":
        return op[1], None
    if kind == "lstrip":
        ch = op[1]
        if not text.startswith(ch):
            return None, "no leading %r" % ch
        return text[len(ch):], None
    return None, "unknown op " + kind

ops = {}   # (book,chunk,seg) -> list of (gid, op)
skips = [] # (gid, book, chunk, seg, reason)
mis = []
errors = []

for e in ents:
    k = (e["book"], e["chunk"], e["seg"])
    gid = e["gid"]
    dkey = gid + "|" + e["type"]
    op = D.get(dkey) or D.get(gid)
    if op is not None:
        if op[0] == "auto":
            pairs = [p for p in e["pairs"] if p[0] in ("將A改為B", "A改為B", "刪除")]
            cur = e["current"] or ""
            for p in pairs:
                if p[1] and p[1] in cur:
                    ops.setdefault(k, []).append((gid, ("apply", p[1], p[2])))
            continue
        if op[0] == "skip":
            skips.append((gid, e["book"], e["chunk"], e["seg"], op[1]))
        elif op[0] == "mis":
            mis.append((gid, e["book"], e["chunk"], e["seg"], e["suggestion"], op[1]))
        else:
            ops.setdefault(k, []).append((gid, op))
        continue
    # auto clean
    pairs = [p for p in e["pairs"] if p[0] in ("將A改為B", "A改為B", "刪除")]
    cur = e["current"] or ""
    good = [p for p in pairs if p[1] and p[1] in cur]
    if good:
        for p in good:
            ops.setdefault(k, []).append((gid, ("apply", p[1], p[2])))
    else:
        errors.append("UNHANDLED %s seg=%d %s" % (gid, e["seg"], e["type"]))

# apply per segment in deterministic order
rows = []
applied_entries = 0
for k in sorted(ops):
    book, chunk, seg = k
    base = paras(book, chunk)[seg - 1]
    text = base
    changed = False
    for gid, op in ops[k]:
        new, err = apply_op(text, op, gid)
        if err:
            errors.append("FAIL %s seg=%d: %s" % (gid, seg, err))
            continue
        if new == text:
            errors.append("NOCHANGE %s seg=%d" % (gid, seg))
            continue
        text = new
        changed = True
        applied_entries += 1
    if changed:
        assert "\n" not in text and "\r" not in text
        rows.append((book, chunk, seg, text, base))

io.open(os.path.join(OUT, "rows.json"), "w", encoding="utf-8").write(
    json.dumps([{"book": b, "chunk": c, "seg": s, "new": t, "old": o} for b, c, s, t, o in rows],
               ensure_ascii=False, indent=1))
io.open(os.path.join(OUT, "applied.json"), "w", encoding="utf-8").write(
    json.dumps([{"gid": g, "book": b, "chunk": c, "seg": s2, "op": o[0]} for (b, c, s2), lst in ops.items() for g, o in lst], ensure_ascii=False, indent=1))
io.open(os.path.join(OUT, "skips.json"), "w", encoding="utf-8").write(
    json.dumps(skips, ensure_ascii=False, indent=1))
io.open(os.path.join(OUT, "mis.json"), "w", encoding="utf-8").write(
    json.dumps(mis, ensure_ascii=False, indent=1))

print("rows:", len(rows), "applied entries:", applied_entries, "skips:", len(skips), "mis:", len(mis))
print("errors:", len(errors))
for x in errors:
    print("  ", x)
