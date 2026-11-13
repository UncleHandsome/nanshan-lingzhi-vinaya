# -*- coding: utf-8 -*-
"""套用 edits_all.json（乾跑 / 寫入）。用法: python run.py check | python run.py write"""
import os, sys, json, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit2

HERE = os.path.dirname(os.path.abspath(__file__))
ORDER = ["695", "698", "699", "700", "701", "804", "841", "1098", "1112", "1207", "1250", "1256"]


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    edits = json.loads(io.open(os.path.join(HERE, "edits_all.json"), encoding="utf-8").read())
    for nnn in ORDER:
        segs = {s["no"]: s for s in kit2.parse7k(nnn)}
        bad = []
        for no, pairs in edits[nnn].items():
            s = segs[no]
            cur = kit2.cur_text(s)
            tmp = cur
            for p in pairs:
                c = tmp.count(p["find"])
                if c != 1:
                    bad.append((no, c, p["find"]))
                tmp = tmp.replace(p["find"], p["new"])
        print("%s: %d 段, 問題 %d" % (nnn, len(edits[nnn]), len(bad)))
        for b in bad:
            print("   !! %s count=%d %r" % b)
        if mode == "check" and not bad:
            for no in edits[nnn]:
                s = segs[no]
                cur = kit2.cur_text(s)
                new = cur
                for p in edits[nnn][no]:
                    new = new.replace(p["find"], p["new"])
                print("   %s %s#%d" % (no, s["chunk"], s["idx"]))
                print("     - " + cur)
                print("     + " + new)
        if mode == "write":
            if bad:
                raise SystemExit("有 FIND 問題，停止")
            kit2.apply_edits(nnn, edits[nnn])


if __name__ == "__main__":
    main()
