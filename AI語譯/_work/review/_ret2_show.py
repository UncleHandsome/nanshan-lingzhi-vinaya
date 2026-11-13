# -*- coding: utf-8 -*-
"""列出指定 chunk#idx 的段落內容，並檢查 idx 與行號關係。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _ret2_lib as L


def main(spec):
    for s in spec:
        chunk, idx = s.split("#")
        idx = int(idx)
        p, t = L.load(chunk)
        ps = L.paras(t)
        # 行號：段落起始行
        if idx < 1 or idx > len(ps):
            print("!! %s#%d out of range (paras=%d)" % (chunk, idx, len(ps)))
            continue
        line = sum(x.count("\n") + 2 for x in ps[:idx - 1]) + 1
        print("==== %s#%d  [%s  line %d, paras=%d] ====" % (chunk, idx, os.path.basename(p), line, len(ps)))
        print(ps[idx - 1])
        print()


if __name__ == "__main__":
    main(sys.argv[1:])
