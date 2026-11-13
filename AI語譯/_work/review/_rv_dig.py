# -*- coding: utf-8 -*-
"""把 resp_NNN.txt 切成「段＋條目」，標出該段現行是否已異動，並抽出有錯誤主張的條目。
用法: python _rv_dig.py 895 896 ... > _rv_dig.txt
"""
import os, sys, re, io, json

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
sys.path.insert(0, os.path.join(ROOT, "AI語譯", "_work", "review"))
from _rv_kit import parse_x7, cur_of  # noqa

RESP = os.path.join(ROOT, "batch_qwen", "r7k")

ERR = re.compile(
    r"誤|錯|讀反|相反|顛倒|反了|倒裝|生造|失義|丟[了失]|漏|窄|偏離|主語|指代|對象|因果|範圍|術語|專名|法數|衍|添譯|增譯|不宜|應為|應作|不符|矛盾|不通|講反|理解錯|坐實|張冠李戴|無據|非原文|原意")
KEEP = re.compile(r"建議|可斟酌|可作|必改|必查|統一|加注|補注|括注|體例|引號|篇題|牒")


def split_items(text):
    """回傳 [(segno, item_text)]"""
    out = []
    cur_seg = None
    buf = []
    for ln in text.split("\n"):
        m = re.match(r"^#+\s*【(\d{3,4}-\d{4})】", ln.strip())
        if m:
            if buf and cur_seg:
                out.append((cur_seg, "\n".join(buf).strip()))
            cur_seg = m.group(1)
            buf = [ln.strip()]
            continue
        if cur_seg is None:
            continue
        if ln.strip().startswith("## ") or ln.strip().startswith("#"):
            if buf:
                out.append((cur_seg, "\n".join(buf).strip()))
            buf = []
            cur_seg = None
            continue
        buf.append(ln.rstrip())
    if buf and cur_seg:
        out.append((cur_seg, "\n".join(buf).strip()))
    return out


def main(nnns):
    res = []
    for nnn in nnns:
        p = os.path.join(RESP, "resp_%s.txt" % nnn)
        text = io.open(p, encoding="utf-8").read()
        segs = {s["no"]: s for s in parse_x7(nnn)}
        for no, body in split_items(text):
            s = segs.get(no)
            status = "?"
            if s:
                status = "同" if (cur_of(s) == s["tr"]) else "改"
            res.append({"file": nnn, "no": no, "status": status, "body": body})
    json.dump(res, io.open(os.path.join(ROOT, "AI語譯", "_work", "review", "_rv_items.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("items=%d" % len(res))
    from collections import Counter
    c = Counter((r["file"], r["status"]) for r in res)
    print(" ".join("%s:%s=%d" % (k[0], k[1], v) for k, v in sorted(c.items())))


if __name__ == "__main__":
    nnns = [str(x) for x in range(int(sys.argv[1]), int(sys.argv[2]) + 1)] if len(sys.argv) == 3 else sys.argv[1:]
    main(nnns)
