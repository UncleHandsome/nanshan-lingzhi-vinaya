# -*- coding: utf-8 -*-
"""預覽：套用後各段前後對照（不寫檔）。"""
import sys, os, difflib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _ret2_lib as L
import _ret2_apply as A


def main():
    by_chunk = {}
    for it, ch, idx, old, new in A.EDITS:
        by_chunk.setdefault(ch, {}).setdefault(idx, []).append((it, old, new))
    for ch, m in by_chunk.items():
        p, t = L.load(ch)
        ps = L.paras(t)
        for idx in sorted(m):
            s = ps[idx - 1]
            for it, old, new in m[idx]:
                s = s.replace(old, new)
            print("==== %s#%d  %s ====" % (ch, idx, "/".join(x[0] for x in m[idx])))
            print("【原文】", end="")
            src = _src_of(ch, idx)
            print(src[:120] if src else "(略)")
            print("【改後】")
            print(s)
            print()


def _src_of(ch, idx):
    return ""


if __name__ == "__main__":
    main()
