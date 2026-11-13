# -*- coding: utf-8 -*-
"""把卷中之三 50 檔登記進 batch_qwen/r7k_done.tsv（先移除本輪先前誤用舊格式寫入的列）。"""
import io, json, os

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
VIEW = os.path.join(ROOT, "AI語譯", "_work", "review", "_r7k_view")
P = os.path.join(ROOT, "batch_qwen", "r7k_done.tsv")

FILES = ["edits_07a.json", "edits_07b.json", "edits_07b2.json", "edits_07c.json",
         "edits_07c2.json", "edits_07c3.json", "edits_07d.json", "edits_07d2.json"]

seg_ops = {}
for f in FILES:
    d = json.load(io.open(os.path.join(VIEW, f), encoding="utf-8"))
    for no, ops in d.items():
        seg_ops[no] = len(ops)

by_file = {}
for no, n in seg_ops.items():
    fl = no.split("-")[0]
    by_file.setdefault(fl, [0, 0])
    by_file[fl][0] += 1      # 段數
    by_file[fl][1] += n      # 改處

CHUNK = {}
for n in range(207, 257):
    if n <= 218:
        CHUNK[n] = "07a_卷中之三"
    elif n <= 230:
        CHUNK[n] = "07b_卷中之三"
    elif n == 231:
        CHUNK[n] = "07b/07c"
    elif n <= 243:
        CHUNK[n] = "07c_卷中之三"
    elif n == 244:
        CHUNK[n] = "07c/07d"
    else:
        CHUNK[n] = "07d_卷中之三"

REJECT = {207: 15, 208: 17, 209: 14, 210: 14, 211: 20, 212: 12, 213: 11, 214: 24, 215: 20,
          216: 15, 217: 16, 218: 12, 219: 8, 220: 18, 221: 11, 222: 9, 223: 21, 224: 21,
          225: 10, 226: 18, 227: 23, 228: 17, 229: 20, 230: 13, 231: 22, 232: 16, 233: 21,
          234: 10, 235: 26, 236: 38, 237: 11, 238: 15, 239: 24, 240: 11, 241: 14, 242: 7,
          243: 18, 244: 11, 245: 8, 246: 5, 247: 12, 248: 10, 249: 9, 250: 20, 251: 10,
          252: 6, 253: 16, 254: 12, 255: 10, 256: 16}
DOUBT = {219: 1, 236: 2}

raw = io.open(P, encoding="utf-8", newline="").read()
eol = "\r\n" if "\r\n" in raw else "\n"
lines = raw.split(eol)
if lines and lines[-1] == "":
    lines = lines[:-1]

# 移除先前以舊 5 欄格式誤寫的「卷中之三」列
kept = []
removed = 0
for ln in lines:
    c = ln.split("\t")
    if len(c) == 5 and c[1] == "卷中之三":
        removed += 1
        continue
    kept.append(ln)

rows = []
for n in range(207, 257):
    fl = "%03d" % n
    seg, ops = by_file.get(fl, [0, 0])
    bak = "歸檔/7K卷修正前/01_行事鈔/%s_v.txt" % CHUNK[n].split("/")[0]
    rows.append("\t".join([fl, CHUNK[n], str(seg), str(ops), str(REJECT[n]), str(DOUBT.get(n, 0)), bak, "完成"]))

out = eol.join(kept + rows) + eol
io.open(P, "w", encoding="utf-8", newline="").write(out)
print("removed", removed, "old-format rows; appended", len(rows))
