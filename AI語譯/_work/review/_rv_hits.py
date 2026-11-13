# -*- coding: utf-8 -*-
"""resp 段落級抽取：保留同時含「段號」與「錯誤主張」關鍵詞的段落。
用法: python _rv_hits.py 895 896 ..."""
import os, sys, re, io

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
RESP = os.path.join(ROOT, "batch_qwen", "r7k")
VIEW = os.path.join(ROOT, "AI語譯", "_work", "review", "_rv_view")

ERR = re.compile(r"誤|錯|讀反|相反|顛倒|反了|生造|失義|丟[了失]|漏|窄|偏離|主語|指代|對象|因果|範圍|術語|專名|法數|衍|添譯|增譯|不宜|應為|應作|不符|矛盾|不通|講反|理解錯|坐實|張冠李戴|無據|原意|必改|必查|泛譯|意譯|失準|不當|不是|並非|混|倒置|移就|主體")
SEG = re.compile(r"(\d{4})-(\d{4})")


def main(nnns):
    if not os.path.isdir(VIEW):
        os.makedirs(VIEW)
    for n in nnns:
        p = os.path.join(RESP, "resp_%s.txt" % n)
        text = io.open(p, encoding="utf-8").read()
        paras = [x.strip() for x in re.split(r"\n\s*\n", text) if x.strip()]
        buf = ["#" * 8 + " hits %s " % n + "#" * 8]
        nh = 0
        for i, pa in enumerate(paras):
            if not SEG.search(pa):
                continue
            if not ERR.search(pa):
                continue
            nh += 1
            buf.append("\n[%d] %s" % (i, pa))
        io.open(os.path.join(VIEW, "hits_%s.txt" % n), "w", encoding="utf-8").write("\n".join(buf) + "\n")
        print("%s paras=%d hits=%d chars=%d" % (n, len(paras), nh, len("\n".join(buf))))


if __name__ == "__main__":
    main(sys.argv[1:])
