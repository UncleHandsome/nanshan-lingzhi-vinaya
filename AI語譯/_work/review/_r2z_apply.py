# -*- coding: utf-8 -*-
"""Apply judged substring rewrites to out/資持記/<chunk>.txt paragraphs.

edits.json: [{"chunk": "...", "seg": N, "reps": [["old","new"], ...], "note": "..."}]
Each old substring must occur exactly once in that paragraph; the rest is copied verbatim.
Backs up chunk file to 歸檔/r2修正前/資持記/ before first write.
"""
import io, os, json, sys, shutil

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUTD = os.path.join(ROOT, "AI語譯", "out", "資持記")
BAK = os.path.join(ROOT, "歸檔", "r2修正前", "資持記")


def main():
    edits = json.load(io.open(sys.argv[1], encoding="utf-8"))
    dry = "--dry" in sys.argv
    by_chunk = {}
    for e in edits:
        by_chunk.setdefault(e["chunk"], []).append(e)
    os.makedirs(BAK, exist_ok=True)
    changed = 0
    for chunk, es in by_chunk.items():
        p = os.path.join(OUTD, chunk + ".txt")
        lines = io.open(p, encoding="utf-8").read().split("\n")
        idx = [i for i, l in enumerate(lines) if l.strip()]
        if len(idx) < max(e["seg"] for e in es):
            print("!! seg out of range", chunk, len(idx))
            continue
        bak = os.path.join(BAK, chunk + ".txt")
        if not os.path.exists(bak):
            shutil.copy2(p, bak)
        for e in es:
            i = idx[e["seg"] - 1]
            s = lines[i]
            ok = True
            for old, new in e["reps"]:
                c = s.count(old)
                if c != 1:
                    print("!! REP COUNT", c, chunk, e["seg"], repr(old[:40]))
                    ok = False
                    break
                s = s.replace(old, new)
            if not ok or s == lines[i]:
                continue
            lines[i] = s
            changed += 1
            print("ok %s #%d  %d -> %d" % (chunk, e["seg"], len(lines[i]), len(s)))
        if not dry:
            io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    print("changed paragraphs:", changed)


main()
