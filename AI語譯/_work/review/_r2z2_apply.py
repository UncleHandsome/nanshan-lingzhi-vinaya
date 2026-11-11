# -*- coding: utf-8 -*-
"""Apply r2 zhichi edits: JSON list of {chunk,seg,old,new,why}.

usage: python _r2z2_apply.py edits.json [--dry]
Each edit is a substring replacement inside one segment line (segment index = k,
file line = 2k-1). Verifies old occurs exactly once in that segment.
Appends applied log to _r2z2_log.jsonl.
"""
import os, re, io, sys, json, shutil, datetime

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUTD = os.path.join(ROOT, "AI語譯", "out", "資持記")
BAK = os.path.join(ROOT, "歸檔", "r2修正前", "資持記")
REV = os.path.join(ROOT, "AI語譯", "_work", "review")
LOG = os.path.join(REV, "_r2z2_log.jsonl")

def seg_lines(text):
    """return list of (file_lineno, text) for non-empty lines"""
    out = []
    for i, l in enumerate(text.split("\n")):
        if l.strip():
            out.append((i, l))
    return out

def main():
    p = sys.argv[1]
    dry = "--dry" in sys.argv
    edits = json.load(io.open(p, encoding="utf-8"))
    by_chunk = {}
    for e in edits:
        by_chunk.setdefault(e["chunk"], []).append(e)
    os.makedirs(BAK, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report = []
    for chunk, es in by_chunk.items():
        path = os.path.join(OUTD, chunk + ".txt")
        text = io.open(path, encoding="utf-8").read()
        sl = seg_lines(text)
        lines = text.split("\n")
        ok = True
        buf = dict(enumerate(lines))
        for e in es:
            k = e["seg"]
            if k < 1 or k > len(sl):
                report.append(("ERR", chunk, k, "seg out of range"))
                ok = False
                continue
            fno, cur = sl[k - 1]
            if "set" in e:
                buf[fno] = e["set"]
                sl[k - 1] = (fno, buf[fno])
                report.append(("OK", chunk, k, "SET " + e["set"][:24]))
                continue
            old, new = e["old"], e["new"]
            c = cur.count(old)
            if c != 1:
                report.append(("ERR", chunk, k, f"old count={c}: {old[:30]}"))
                ok = False
                continue
            buf[fno] = cur.replace(old, new)
            sl[k - 1] = (fno, buf[fno])
            report.append(("OK", chunk, k, f"{old[:24]} => {new[:24]}"))
        if dry or not ok:
            for r in report:
                if r[0] == "ERR" or dry:
                    print(*r)
            if not ok:
                print("!! abort chunk", chunk)
            continue
        newtext = "\n".join(buf[f] for f in sorted(buf))
        if not dry:
            if not os.path.exists(os.path.join(BAK, chunk + ".txt")):
                shutil.copy2(path, os.path.join(BAK, chunk + ".txt"))
            io.open(path, "w", encoding="utf-8", newline="").write(newtext)
        print("applied", chunk, len(es), "edits")
        with io.open(LOG, "a", encoding="utf-8") as f:
            for e in es:
                f.write(json.dumps({"t": stamp, **e}, ensure_ascii=False) + "\n")
    print("done", len(edits), "edits")

main()
