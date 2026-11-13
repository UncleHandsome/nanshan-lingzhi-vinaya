# -*- coding: utf-8 -*-
"""Apply 7K 卷四之四 edits.

edits JSON format:
{ "03_業疏/21a_卷四之四": [ {"no": "2761-0001", "idx": 10, "ops": [{"find": "...", "new": "..."}]} ] }

Usage:
  python _r7k_v44_apply.py edits_2761_2766.json          # dry-run diff
  python _r7k_v44_apply.py edits_2761_2766.json --write  # write + backup
"""
import os, re, io, sys, json, shutil

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT, "AI語譯", "out")
BAK = os.path.join(ROOT, "歸檔", "7K卷修正前")


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def wr(p, s):
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def main():
    efs = [a for a in sys.argv[1:] if not a.startswith("--")]
    write = "--write" in sys.argv
    edits = {}
    for ef in efs:
        for k, v in json.loads(rd(ef)).items():
            edits.setdefault(k, []).extend(v)
    total = 0
    for chunk, items in edits.items():
        book, name = chunk.split("/", 1)
        p = os.path.join(OUT, book, name + ".txt")
        raw = rd(p)
        eol = "\r\n" if "\r\n" in raw else "\n"
        lines = raw.split(eol)
        idxs = [i for i, l in enumerate(lines) if l.strip()]
        for it in items:
            i = idxs[it["idx"] - 1]
            old = lines[i]
            cur = old
            for op in it["ops"]:
                find, new = op["find"], op["new"]
                c = cur.count(find)
                if c != 1:
                    raise SystemExit("FIND count=%d %s #%d %r" % (c, it["no"], it["idx"], find))
                cur = cur.replace(find, new)
            if cur == old:
                raise SystemExit("NOCHANGE %s #%d" % (it["no"], it["idx"]))
            print("=" * 60)
            print("%s #%d" % (it["no"], it["idx"]))
            print("- 舊: " + old)
            print("+ 新: " + cur)
            lines[i] = cur
            total += 1
        if write:
            d = os.path.join(BAK, book)
            if not os.path.isdir(d):
                os.makedirs(d)
            bp = os.path.join(d, name + "_v.txt")
            if not os.path.exists(bp):
                shutil.copy2(p, bp)
                print("[備份] %s" % os.path.relpath(bp, ROOT))
            wr(p, eol.join(lines))
            print("[寫入] %s  %d 段" % (chunk, len(items)))
    print("TOTAL %d" % total)


if __name__ == "__main__":
    main()
