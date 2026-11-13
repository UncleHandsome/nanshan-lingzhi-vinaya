# -*- coding: utf-8 -*-
"""以文字片段定位段號（校閱_7K/校閱_8xx.txt）並顯示原文／現行。
用法: python _rv2_loc.py "要搜的字串" [..]
"""
import os, sys, re, io, glob

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
sys.path.insert(0, os.path.join(ROOT, "AI語譯", "_work", "review"))
from _rv_kit import parse_x7, cur_of  # noqa

X7 = os.path.join(ROOT, "校閱_7K")


def locate(needle):
    hits = 0
    for p in sorted(glob.glob(os.path.join(X7, "校閱_8*.txt"))):
        nnn = re.search(r"校閱_(\d+)\.txt", p).group(1)
        lines = io.open(p, encoding="utf-8").read().split("\n")
        for i, ln in enumerate(lines):
            if needle not in ln:
                continue
            # 往上找段號與原文
            no = None
            src = ""
            for j in range(i, -1, -1):
                s = lines[j].strip()
                m = re.match(r"^【(\d{3,4}-\d{4})】", s)
                if m:
                    no = m.group(1)
                    for k in range(j, i + 1):
                        if lines[k].startswith("【原文】"):
                            src = lines[k][4:].strip()
                    break
            hits += 1
            print("%s  %s:%d" % (no, nnn, i + 1))
            print("  原文: " + (src if len(src) <= 300 else src[:300] + "…"))
            segs = {s["no"]: s for s in parse_x7(nnn)}
            if no and no in segs:
                print("  現行: " + cur_of(segs[no]))
            print()
    print("hits=%d" % hits)


if __name__ == "__main__":
    for n in sys.argv[1:]:
        print("### " + n)
        locate(n)
