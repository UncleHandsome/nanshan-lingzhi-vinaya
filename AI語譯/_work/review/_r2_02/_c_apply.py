# -*- coding: utf-8 -*-
"""Apply c-pass edits: chunk -> read current -> replace inside one paragraph -> write back.

ops JSON: [{"chunk": "...", "seg": 1, "old": "...", "new": "...", "note": "..."}]
Backup: 歸檔/r2修正前/02_戒疏/<name>.txt (add _c, _c2 ... if exists).
"""
import io, os, re, sys, json, shutil, datetime

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
HERE = os.path.join(ROOT, "AI語譯", "_work", "review", "_r2_02")
OUTD = os.path.join(ROOT, "AI語譯", "out", "02_戒疏")
ARCH = os.path.join(ROOT, "歸檔", "r2修正前", "02_戒疏")
LOG = os.path.join(HERE, "_c_log.jsonl")


def read_raw(chunk):
    return io.open(os.path.join(OUTD, chunk + ".txt"), encoding="utf-8", newline="").read()


def split_paras(t):
    sep = "\r\n\r\n" if "\r\n\r\n" in t else "\n\n"
    return t.split(sep), sep


def backup(chunk):
    os.makedirs(ARCH, exist_ok=True)
    base = chunk + ".txt"
    if os.path.exists(os.path.join(ARCH, chunk + "_c.txt")):
        return None
    dst = os.path.join(ARCH, base)
    n = 0
    while os.path.exists(dst):
        n += 1
        dst = os.path.join(ARCH, "%s_c%s.txt" % (chunk, "" if n == 1 else str(n)))
    shutil.copy2(os.path.join(OUTD, base), dst)
    return dst


def apply(ops):
    by = {}
    for o in ops:
        by.setdefault(o["chunk"], []).append(o)
    log = []
    for chunk, lst in by.items():
        t = read_raw(chunk)
        parts, sep = split_paras(t)
        made = None
        for o in lst:
            s = o["seg"]
            if not (0 < s <= len(parts)):
                print("OUT_OF_RANGE", chunk, s); continue
            p = parts[s - 1]
            c = p.count(o["old"])
            if c != 1:
                print("MISS/DUP(%d)" % c, chunk, s, o["old"][:40]); continue
            parts[s - 1] = p.replace(o["old"], o["new"], 1)
            if made is None:
                made = backup(chunk) or "-"
            log.append({"ts": datetime.datetime.now().isoformat(timespec="seconds"),
                        "chunk": chunk, "seg": s, "old": o["old"], "new": o["new"],
                        "note": o.get("note", "")})
        if made is not None:
            new = sep.join(parts)
            io.open(os.path.join(OUTD, chunk + ".txt"), "w", encoding="utf-8", newline="").write(new)
            print("WROTE", chunk, "edits", len(lst), "backup", os.path.basename(made))
    if log:
        with io.open(LOG, "a", encoding="utf-8") as f:
            for x in log:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")
    print("applied", len(log), "of", len(ops))


if __name__ == "__main__":
    ops = json.load(io.open(sys.argv[1], encoding="utf-8"))
    apply(ops)
