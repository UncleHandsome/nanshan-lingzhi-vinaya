# -*- coding: utf-8 -*-
"""Verify fix_err2_g3.tsv: shape, char safety, and show minimal diffs."""
import io, os, difflib

BASE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(BASE, "report_err2.tsv")
OUT = os.path.join(BASE, "fix_err2_g3.tsv")


def rows(path):
    with io.open(path, encoding="utf-8-sig") as f:
        lines = f.read().split("\n")
    hdr = lines[0].rstrip("\r").split("\t")
    out = []
    for ln in lines[1:]:
        ln = ln.rstrip("\r")
        if not ln.strip():
            continue
        f = ln.split("\t")
        if len(f) == len(hdr):
            out.append(dict(zip(hdr, f)))
    return out


rep = [r for r in rows(REPORT) if r["book"] == "02_戒疏"]
with io.open(OUT, encoding="utf-8") as f:
    raw = f.read()
lines = raw.split("\n")
assert lines[-1] == "", "file must end with newline"
lines = lines[:-1]
print("out lines:", len(lines))
bad = 0
seen = []
for i, ln in enumerate(lines):
    parts = ln.split("\t")
    assert len(parts) == 4, (i, len(parts))
    book, chunk, seg, new = parts
    assert book == "02_戒疏"
    assert "\n" not in new and "\r" not in new
    seen.append((chunk, seg))
    cur = None
    for r in rep:
        if r["chunk"] == chunk and r["seg"] == seg:
            cur = r["current"]
            break
    assert cur is not None, (chunk, seg)
    if new == cur:
        print("UNCHANGED", chunk, seg)
        bad += 1
    sm = difflib.SequenceMatcher(None, cur, new, autojunk=False)
    ops = [op for op in sm.get_opcodes() if op[0] != "equal"]
    print(f"--- {chunk} seg{seg}  {len(ops)} change block(s)")
    for tag, i1, i2, j1, j2 in ops:
        print(f"  - {cur[i1:i2]!r}")
        print(f"  + {new[j1:j2]!r}")
print("seen keys:", seen)
print("bad:", bad)
