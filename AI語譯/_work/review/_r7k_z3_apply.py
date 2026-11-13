# -*- coding: utf-8 -*-
"""Apply 卷下之一 edits with validation.
usage: python _r7k_z3_apply.py [--dry]
"""
import os, io, json, shutil, glob, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
REV = os.path.join(ROOT, r"AI語譯\_work\review")
OUT = os.path.join(ROOT, "AI語譯", "out", "01_行事鈔")
BAK = os.path.join(ROOT, "歸檔", "7K卷修正前", "01_行事鈔")

DEC_FILES = ["_r7k_z3_dec.json", "_r7k_z3_dec2.json", "_r7k_z3_dec3.json",
             "_r7k_z3_dec4.json", "_r7k_z3_dec5.json", "_r7k_z3_dec6.json",
             "_r7k_z3_dec7.json", "_r7k_z3_dec8.json", "_r7k_z3_dec9.json",
             "_r7k_z3_dec10.json", "_r7k_z3_dec11.json", "_r7k_z3_dec12.json",
             "_r7k_z3_dec13.json", "_r7k_z3_dec14.json", "_r7k_z3_dec15.json",
             "_r7k_z3_dec16.json", "_r7k_z3_dec17.json", "_r7k_z3_dec18.json"]


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def main(dry):
    plan = {}
    stats = []
    for df in DEC_FILES:
        p = os.path.join(REV, df)
        d = json.loads(rd(p))
        for fno, rec in d.items():
            ch = rec["chunk"]
            if not rec["changed_idx"]:
                stats.append((fno, ch, rec["segs"], 0, len(rec["changed_idx"]), rec["rejected"], len(rec["doubts"])))
                continue
            plan.setdefault(ch, {})
            for idx_s, ops in rec["ops"].items():
                plan[ch].setdefault(int(idx_s), {"ops": [], "files": []})
                plan[ch][int(idx_s)]["ops"].extend((o[0], o[1], o[2] if len(o) > 2 else 1) for o in ops)
                plan[ch][int(idx_s)]["files"].append(fno)
            stats.append((fno, ch, rec["segs"], 0, len(rec["changed_idx"]), rec["rejected"], len(rec["doubts"])))

    total_lines = 0
    for ch, segmap in plan.items():
        p = os.path.join(OUT, ch + ".txt")
        raw = rd(p)
        eol = "\r\n" if "\r\n" in raw else "\n"
        lines = raw.split(eol)
        idxs = [i for i, l in enumerate(lines) if l.strip()]
        before = {}
        for idx, rec in sorted(segmap.items()):
            try:
                li = idxs[idx - 1]
            except IndexError:
                print("!! %s #%d out of range (nonempty=%d)" % (ch, idx, len(idxs)))
                raise SystemExit(1)
            old = lines[li]
            before[li] = old
            cur = old
            for find, new, n in rec["ops"]:
                c = cur.count(find)
                if c != n:
                    print("!! COUNT %s #%d files=%s expect=%d got=%d FIND=%r" % (ch, idx, rec["files"], n, c, find))
                    raise SystemExit(1)
                if find == new:
                    print("!! NOOP %s #%d FIND=%r" % (ch, idx, find))
                    raise SystemExit(1)
                cur = cur.replace(find, new)
            if cur == old:
                print("!! UNCHANGED %s #%d" % (ch, idx))
                raise SystemExit(1)
            lines[li] = cur
            total_lines += 1
        print("%s: %d 段待改（非空行 %d）" % (ch, len(segmap), len(idxs)))
        if not dry:
            if not os.path.isdir(BAK):
                os.makedirs(BAK)
            bp = os.path.join(BAK, ch + "_v.txt")
            if not os.path.exists(bp):
                shutil.copy2(p, bp)
                print("  備份 -> %s" % os.path.relpath(bp, ROOT))
            with io.open(p, "w", encoding="utf-8", newline="") as f:
                f.write(eol.join(lines))
            print("  寫入，行數 %d -> %d" % (len(raw.split(eol)), len(lines)))
    print("\n改動行合計", total_lines)
    for s in stats:
        print("%s\t%s\t%d segs\t%d changed\t%d reject\t%d doubt" % (s[0], s[1], s[2], s[4], s[5], s[6]))


if __name__ == "__main__":
    main("--dry" in sys.argv)
