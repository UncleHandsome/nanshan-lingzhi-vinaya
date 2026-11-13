# -*- coding: utf-8 -*-
"""套用後驗證：備份逐段比對、段數/行數/行尾、改動段清單。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _ret3_lib as L
import _ret3_apply as A

BAK = os.path.join(L.ROOT, "歸檔", "ret3套用_04比丘尼鈔_修正前")


def main():
    by_chunk = {}
    for e in A.EDITS:
        by_chunk.setdefault(e["chunk"], []).append(e)
    allok = True
    for chunk, es in sorted(by_chunk.items()):
        p, t = L.load(chunk)
        bp = os.path.join(BAK, os.path.basename(p))
        old = open(bp, encoding="utf-8", newline="").read()
        ps, po = L.paras(t), L.paras(old)
        assert len(ps) == len(po), chunk
        diff = [i + 1 for i in range(len(ps)) if ps[i] != po[i]]
        want = sorted({e["para"] for e in es})
        st = (t.count("\n") == old.count("\n"), t.count("\r") == old.count("\r") == 0)
        print("%-4s paras %d==%d  changed=%s  want=%s  lines/CR ok=%s" %
              (chunk, len(ps), len(po), diff, want, st))
        if diff != want or not all(st):
            print("  !! MISMATCH"); allok = False
        # 確認 new 已在段中
        nt = "\n\n".join(ps)
        for e in es:
            if e["new"] not in ps[e["para"] - 1]:
                print("  !! new missing", e["eid"]); allok = False
            if e["old"] in nt:
                print("  !! old still present", e["eid"]); allok = False
    # 未動檔
    for c in ["01b", "02b", "04a", "04b", "06a", "06b"]:
        pass
    print("ALL OK:", allok)


if __name__ == "__main__":
    main()
