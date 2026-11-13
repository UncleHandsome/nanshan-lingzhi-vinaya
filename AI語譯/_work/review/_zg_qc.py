# -*- coding: utf-8 -*-
"""Final QC for 中三下 補缺: duplicate 6-grams, punctuation runs, 字以下 counts."""
import io
import os
from collections import Counter

import _z6_lib as L

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "_zg_qc.txt")


def main():
    rows = []
    for chunk, lo, hi in (("10b_中三下", 7, 64), ("10c_中三下", 1, 9)):
        t, s = L.paras(chunk)
        ps = t.split(s)
        rows.append("%s paras=%d lines=%d" % (chunk, len(ps), t.count("\n")))
        for p in range(lo, hi + 1):
            txt = ps[p - 1]
            # duplicate 6-grams
            grams = Counter()
            for i in range(len(txt) - 5):
                grams[txt[i:i + 6]] += 1
            dups = sorted(g for g, c in grams.items() if c > 1 and "，" not in g and "。" not in g)
            flags = []
            if dups:
                flags.append("DUP6=" + "|".join(dups[:6]))
            for bad in (u"，，", u"。。", u"的的", u"是是", u"在在"):
                if bad in txt:
                    flags.append("PUNCT=" + bad)
            n = txt.count(u"字以下")
            if flags:
                rows.append("%s#%d n=%d %s" % (chunk, p, n, " ".join(flags)))
    with io.open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(rows))


if __name__ == "__main__":
    main()
