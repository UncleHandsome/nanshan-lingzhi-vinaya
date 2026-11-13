# -*- coding: utf-8 -*-
"""改後段預覽：逐條套用於記憶體，印出改動前後上下文片段。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _ret3_lib as L
import _ret3_apply as A


def main(width=90):
    by_chunk = {}
    for e in A.EDITS:
        by_chunk.setdefault(e["chunk"], []).append(e)
    for chunk, es in sorted(by_chunk.items()):
        p, t = L.load(chunk)
        ps = L.paras(t)
        print("=" * 30, chunk)
        for e in es:
            i = e["para"] - 1
            new = ps[i].replace(e["old"], e["new"], 1)
            k = new.find(e["new"])
            lo = max(0, k - width)
            hi = min(len(new), k + len(e["new"]) + width)
            print("\n--- %s (para %d) ---" % (e["eid"], e["para"]))
            print(("[...]" if lo else "") + new[lo:hi] + ("[...]" if hi < len(new) else ""))


if __name__ == "__main__":
    main()
