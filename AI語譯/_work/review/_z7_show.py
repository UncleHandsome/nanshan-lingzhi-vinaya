# -*- coding: utf-8 -*-
"""7K 資持記 中四下a：產生 view_<n>.txt（意見＋各段原文/材料譯文/現行狀態）。"""
import io
import os
import sys

import _z6_lib as L

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
RESP = os.path.join(ROOT, "batch_qwen", "r7k")
VIEW = os.path.join(HERE, "_z7_view")


def show(n):
    os.makedirs(VIEW, exist_ok=True)
    buf = []
    rp = os.path.join(RESP, "resp_%d.txt" % n)
    buf.append("#" * 18 + " 意見 resp_%d " % n + "#" * 18)
    if os.path.exists(rp):
        buf.append(L.rd(rp).strip())
    else:
        alt = os.path.join(ROOT, u"待跑_審查擋掉7K", u"回覆", u"檔%d.txt" % n)
        buf.append(L.rd(alt).strip() if os.path.exists(alt) else "(缺意見檔)")
    buf.append("")
    segs = L.mat(n)
    buf.append("#" * 18 + " 段落 %d（%d 段）" % (n, len(segs)) + "#" * 18)
    for s in segs:
        cur = L.para(s["chunk"], s["para"])
        same = "現行=材料" if cur.strip() == s["trans"].strip() else "※現行已異動"
        buf.append("\n--- %s %s#%d [%s]" % (s["idx"], s["chunk"], s["para"], same))
        buf.append("[原文] " + s["orig"])
        buf.append("[材料] " + s["trans"])
        if cur.strip() != s["trans"].strip():
            buf.append("[現行] " + cur)
    out = os.path.join(VIEW, "view_%d.txt" % n)
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(buf) + "\n")
    print("wrote %s  segs=%d" % (out, len(segs)))


if __name__ == "__main__":
    for a in sys.argv[1:]:
        show(int(a))
