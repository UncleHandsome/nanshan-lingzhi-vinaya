# -*- coding: utf-8 -*-
"""驗證：備份 vs 現檔，段數／行數／CR 不變，且變動段限於清單。"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _ret2_lib as L
import _ret2_apply as A

BAK = os.path.join(L.ROOT, "歸檔", "7K卷修正前", "資持記")


def main():
    expect = {}
    for it, ch, idx, old, new in A.EDITS:
        expect.setdefault(ch, set()).add(idx)
    allok = True
    rows = []
    for ch in ["11d", "10b", "14b", "14c", "07d"]:
        p, t = L.load(ch)
        b = os.path.join(BAK, ch + "_ret2_v.txt")
        with open(b, "r", encoding="utf-8", newline="") as f:
            bt = f.read()
        ps, bps = L.paras(t), L.paras(bt)
        assert len(ps) == len(bps), (ch, len(ps), len(bps))
        changed = [i + 1 for i in range(len(ps)) if ps[i] != bps[i]]
        exp = sorted(expect.get(ch, []))
        line_ok = t.count("\n") == bt.count("\n")
        cr_ok = t.count("\r") == 0 and bt.count("\r") == 0
        ok = (changed == exp) and line_ok and cr_ok
        allok &= ok
        print("%s %s paras=%d lines=%d->%d CR=%d changed=%s expect=%s" %
              ("OK " if ok else "!! ", ch, len(ps), bt.count("\n"), t.count("\n"),
               t.count("\r"), changed, exp))
        rows.append((os.path.basename(p), len(ps), len(ps), bt.count("\n"),
                     t.count("\n"), ",".join(map(str, changed)),
                     os.path.getsize(b), os.path.getsize(p)))
    # 全書 LF 掃描（僅本批 5 檔）
    print("ALL OK" if allok else "HAS ERRORS")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_ret2_verify.txt"),
              "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")


if __name__ == "__main__":
    main()
