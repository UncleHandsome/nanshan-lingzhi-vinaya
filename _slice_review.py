# -*- coding: utf-8 -*-
"""把 校閱批次/校閱_XX.txt 依段落邊界切成可供逐段校閱的小片。
每片保留原始標籤、原文、譯文，不改動任何文字。"""
import os, re, json, glob

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "校閱批次")
OUT = os.path.join(SRC, "_切片")
RES = os.path.join(SRC, "校閱結果")
PARTS = os.path.join(RES, "parts")
for d in (OUT, RES, PARTS):
    os.makedirs(d, exist_ok=True)

MAX_BYTES = 165 * 1024   # 每片約 165 KB
MAX_SEGS = 200           # 每片最多 200 段

SEG_RE = re.compile(r"^【\d{2}-\d{4}】")
index = []
for path in sorted(glob.glob(os.path.join(SRC, "校閱_*.txt"))):
    fname = os.path.basename(path)
    stem = os.path.splitext(fname)[0].replace("校閱_", "")
    text = open(path, encoding="utf-8").read()
    lines = text.split("\n")
    starts = [i for i, l in enumerate(lines) if SEG_RE.match(l)]
    segs = []
    for j, i in enumerate(starts):
        end = starts[j + 1] if j + 1 < len(starts) else len(lines)
        block = lines[i:end]
        while block and block[-1].strip() == "":
            block.pop()
        segs.append((lines[i].split("】")[0].lstrip("【"), "\n".join(block)))

    # 分片
    chunks, cur, size = [], [], 0
    for sid, body in segs:
        b = len(body.encode("utf-8"))
        if cur and (size + b > MAX_BYTES or len(cur) >= MAX_SEGS):
            chunks.append(cur); cur, size = [], 0
        cur.append((sid, body)); size += b
    if cur:
        chunks.append(cur)

    # 尾片過小則併回前一片，避免產生只有幾段的碎片任務
    def nbytes(c):
        return sum(len(b.encode("utf-8")) for _, b in c)
    while len(chunks) > 1 and len(chunks[-1]) < 40:
        tail = chunks[-1]
        merged = chunks[-2] + tail
        if nbytes(merged) > 225 * 1024 or len(merged) > 260:
            break
        chunks = chunks[:-2] + [merged]

    pinfo = []
    for k, chunk in enumerate(chunks, 1):
        pname = "%s_p%d" % (stem, k)
        body = ("# 校閱切片　第%s檔 第%d片（原檔：%s）\n"
                "# 本片含 %d 段，編號 %s ～ %s\n"
                "# 來源標籤與編號請原樣照抄；【原文】請逐字複製材料原文。\n\n"
                % (stem, k, fname, len(chunk), chunk[0][0], chunk[-1][0]))
        body += "\n\n".join(b for _, b in chunk) + "\n"
        with open(os.path.join(OUT, pname + ".txt"), "w", encoding="utf-8", newline="\n") as f:
            f.write(body)
        pinfo.append({
            "name": pname,
            "slice": pname + ".txt",
            "report": pname + ".md",
            "segs": len(chunk),
            "first": chunk[0][0],
            "last": chunk[-1][0],
            "ids": [s for s, _ in chunk],
        })
    index.append({"file": fname, "stem": stem, "segs": len(segs), "parts": pinfo})

with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as f:
    json.dump(index, f, ensure_ascii=False, indent=1)

print("檔案數", len(index), "總段數", sum(x["segs"] for x in index),
      "總片數", sum(len(x["parts"]) for x in index))
for x in index:
    print(x["stem"], x["segs"], "→", [p["segs"] for p in x["parts"]])
