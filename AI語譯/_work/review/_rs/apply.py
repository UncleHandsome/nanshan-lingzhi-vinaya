# -*- coding: utf-8 -*-
"""Apply ops: backup, replace inside target paragraphs, preserve newlines; report."""
import io, os, re, json, sys, shutil, collections

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUTD = os.path.join(ROOT, "AI語譯", "out", "02_戒疏")
BAK = os.path.join(ROOT, "歸檔", "潤飾覆核前", "02_戒疏")
HERE = os.path.join(ROOT, "AI語譯", "_work", "review", "_rs")
DRY = "--apply" not in sys.argv

ops = json.load(io.open(os.path.join(HERE, "ops.json"), encoding="utf-8"))

FILES = {}
for f in os.listdir(OUTD):
    if f.endswith(".txt"):
        FILES[f[:-4]] = f

def load(ch):
    p = os.path.join(OUTD, FILES[ch])
    raw = io.open(p, encoding="utf-8", newline="").read()
    if "\r\n" in raw:
        sep, nl = "\r\n\r\n", "\r\n"
    else:
        sep, nl = "\n\n", "\n"
    ps = raw.split(sep)
    tail = ""
    if ps and ps[-1].endswith(nl):
        ps[-1] = ps[-1][: -len(nl)]
        tail = nl
    return raw, ps, sep, nl, tail

# locate ops
plan = []   # (op_idx, chunk, seg)
missing = []
for i, op in enumerate(ops):
    q = op["q"]
    hit = []
    for ch in FILES:
        raw, ps, sep, nl, tail = load(ch)
        for j, p in enumerate(ps):
            if q in p:
                hit.append((ch, j + 1))
    if not hit:
        missing.append((i, op["tag"]))
    for ch, seg in hit:
        plan.append((i, ch, seg))
    op["_hits"] = hit

print("ops", len(ops), "resolved", len(ops) - len(missing), "missing", len(missing))
for i, tag in missing:
    print("  MISSING [%d] %s" % (i, tag))

changed = collections.defaultdict(set)
applied = []
# apply in order; re-load each file each time to see current state
for i, op in enumerate(ops):
    if not op.get("_hits"):
        continue
    q, new = op["q"], op["new"]
    done = 0
    for ch in sorted({h[0] for h in op["_hits"]}):
        raw, ps, sep, nl, tail = load(ch)
        local = 0
        for j, p in enumerate(ps):
            if q in p:
                cnt = p.count(q)
                ps[j] = p.replace(q, new)
                local += cnt
                changed[ch].add(j + 1)
        if local:
            done += local
            if not DRY:
                os.makedirs(BAK, exist_ok=True)
                bp = os.path.join(BAK, FILES[ch][:-4] + "_p.txt")
                if not os.path.exists(bp):
                    shutil.copy2(os.path.join(OUTD, FILES[ch]), bp)
                io.open(os.path.join(OUTD, FILES[ch]), "w", encoding="utf-8", newline="").write(sep.join(ps) + tail)
    applied.append((i, op["tag"], done))

print("applied ops", sum(1 for a in applied if a[2]), "total replacements", sum(a[2] for a in applied))
print("changed chunks", len(changed), "changed paras", sum(len(v) for v in changed.values()))
for ch in sorted(changed):
    print("  %s: %d" % (ch[:3], len(changed[ch])))
json.dump({"changed": {k: sorted(v) for k, v in changed.items()},
           "applied": applied, "dry": DRY},
          io.open(os.path.join(HERE, "apply_log.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
