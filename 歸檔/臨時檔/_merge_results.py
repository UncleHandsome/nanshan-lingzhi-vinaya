# -*- coding: utf-8 -*-
"""合併逐片 AI 精校報告為 01–30 每個原檔一份結果（不含機械預篩）。"""
import os, re, json, glob, collections

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "校閱批次")
IDX = os.path.join(SRC, "_切片", "index.json")
PARTS = os.path.join(SRC, "校閱結果", "parts")
OUT = os.path.join(SRC, "校閱結果")
os.makedirs(OUT, exist_ok=True)

SEG_LINE = re.compile(r"^【(\d{2}-\d{4})】(.+)$")
LIMIT = 30  # 只處理 校閱_01 ～ 校閱_30


def parse_material(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    starts = [i for i, l in enumerate(lines) if SEG_LINE.match(l)]
    return len(starts)


d = [x for x in json.load(open(IDX, encoding="utf-8")) if int(x["stem"]) <= LIMIT]
summary = []
for x in d:
    fname = x["file"]
    nseg = parse_material(os.path.join(SRC, fname))

    ai_text, covered, stats = [], set(), collections.Counter()
    for p in x["parts"]:
        rp = os.path.join(PARTS, p["report"])
        if not os.path.exists(rp):
            continue
        t = open(rp, encoding="utf-8", errors="replace").read()
        if not re.search(r"已檢查\s*\d+\s*段", t):
            continue
        covered.update(p["ids"])
        ai_text.append("<!-- 來源：%s -->\n%s" % (p["report"], t.strip()))
        for m in re.finditer(r"^###\s*(\d{2}-\d{4})｜.*?｜(P[012])｜", t, re.M):
            stats[m.group(2)] += 1
        for m in re.finditer(r"^已檢查\s*\d+\s*段.*?存疑\s*(\d+)\s*條", t, re.M):
            stats["存疑"] += int(m.group(1))

    g = "鈔記" if int(x["stem"]) <= 22 else "戒疏"
    out = ["# %s　校閱結果" % fname, "",
           "- 分組：%s" % g,
           "- 全檔段數：%d" % nseg,
           "- AI 逐段精校（依主提示詞）已覆蓋：%d 段（%.0f%%），共 %d 片" %
           (len(covered), 100.0 * len(covered) / nseg, len(ai_text)),
           "- 精校意見：P0 %d、P1 %d、P2 %d；存疑 %d 條" %
           (stats["P0"], stats["P1"], stats["P2"], stats["存疑"]), "",
           "> 判定依據：`校閱批次/提示詞_白話校閱.md` 主提示詞。"
           "只列有問題的段；標題中的編號與來源標籤照抄材料。", "",
           "---", "", "## 逐段精校意見", "",
           "\n\n".join(ai_text) if ai_text else "（本檔尚無已完成的精校片）", ""]
    with open(os.path.join(OUT, "校閱_%s_結果.md" % x["stem"]), "w",
              encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out))

    summary.append((x["stem"], fname, g, nseg, len(covered),
                    stats["P0"], stats["P1"], stats["P2"], stats["存疑"]))

# 清掉 31–65 的舊結果（那些只有機械預篩，已不需要）
removed = 0
for f in glob.glob(os.path.join(OUT, "校閱_*_結果.md")):
    m = re.search(r"校閱_(\d{2})_結果\.md$", f)
    if m and int(m.group(1)) > LIMIT:
        os.remove(f)
        removed += 1

rows = ["# 白話校閱　總表（01–30）", "",
        "> 依 `校閱批次/提示詞_白話校閱.md` 主提示詞逐段精校；"
        "每條意見附原文、譯文、依據與最小修改建議。31–65 依指示不處理。", "",
        "| 檔 | 分組 | 全檔段 | 已精校 | 覆蓋率 | P0 | P1 | P2 | 存疑 |",
        "|:--|:--|--:|--:|--:|--:|--:|--:|--:|"]
for stem, fname, g, n, cov, p0, p1, p2, k in summary:
    rows.append("| 校閱_%s.txt | %s | %d | %d | %.0f%% | %d | %d | %d | %d |" %
                (stem, g, n, cov, 100.0 * cov / n, p0, p1, p2, k))
rows += ["", "---", "",
         "**合計**：%d 檔、%d 段；已精校 %d 段（%.0f%%）；P0 %d、P1 %d、P2 %d、存疑 %d。" %
         (len(summary), sum(r[3] for r in summary), sum(r[4] for r in summary),
          100.0 * sum(r[4] for r in summary) / sum(r[3] for r in summary),
          sum(r[5] for r in summary), sum(r[6] for r in summary),
          sum(r[7] for r in summary), sum(r[8] for r in summary)), ""]
open(os.path.join(OUT, "總表.md"), "w", encoding="utf-8",
     newline="\n").write("\n".join(rows))

print("已產出 %d 份逐檔結果 + 總表；移除 31–65 舊結果 %d 份" % (len(summary), removed))
print("AI 已精校段數", sum(r[4] for r in summary), "/", sum(r[3] for r in summary))
print("精校意見 P0/P1/P2/存疑", [sum(r[i] for r in summary) for i in (5, 6, 7, 8)])
