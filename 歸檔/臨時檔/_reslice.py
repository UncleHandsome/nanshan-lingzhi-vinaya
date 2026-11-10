# -*- coding: utf-8 -*-
"""把「尚未完成精校」的切片再對半切，降低單次載入量。已完成的片原樣保留。"""
import os, re, json

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "校閱批次")
SL = os.path.join(SRC, "_切片")
PARTS = os.path.join(SRC, "校閱結果", "parts")
IDX = os.path.join(SL, "index.json")

SEG = re.compile(r"^【(\d{2}-\d{4})】")
d = json.load(open(IDX, encoding="utf-8"))
made = 0
for x in d:
    newparts = []
    for p in x["parts"]:
        rp = os.path.join(PARTS, p["report"])
        t = open(rp, encoding="utf-8", errors="replace").read() if os.path.exists(rp) else ""
        done = bool(re.search(r"已檢查\s*\d+\s*段", t))
        if done:
            newparts.append(p)
            continue
        s = open(os.path.join(SL, p["slice"]), encoding="utf-8").read()
        blocks = re.split(r"\n\n(?=【\d{2}-\d{4}】)", s)
        head = blocks[0]
        segs = [b for b in blocks[1:] if SEG.match(b.strip())]
        if len(segs) < 2:
            newparts.append(p)
            continue
        mid = (len(segs) + 1) // 2
        halves = [segs[:mid], segs[mid:]]
        for k, sub in enumerate(halves):
            if not sub:
                continue
            name = "%s_%d" % (p["name"], k + 1)
            ids = [SEG.match(b).group(1) for b in sub]
            nh = head
            nh = re.sub(r"含 \d+ 段", "含 %d 段" % len(sub), nh)
            nh = re.sub(r"編號 \d{2}-\d{4} ～ \d{2}-\d{4}",
                        "編號 %s ～ %s" % (ids[0], ids[-1]), nh)
            body = nh + "\n\n" + "\n\n".join(sub) + "\n"
            open(os.path.join(SL, name + ".txt"), "w", encoding="utf-8",
                 newline="\n").write(body)
            newparts.append({"name": name, "slice": name + ".txt",
                             "report": name + ".md", "segs": len(sub),
                             "first": ids[0], "last": ids[-1], "ids": ids})
            made += 1
    x["parts"] = newparts

json.dump(d, open(IDX, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("新增小片", made, "；總片數", sum(len(x["parts"]) for x in d))
import glob
sizes = [os.path.getsize(f) for f in glob.glob(os.path.join(SL, "*.txt")) if "AGENT" not in f]
print("切片大小：最大", max(sizes), "平均", sum(sizes) // len(sizes))
