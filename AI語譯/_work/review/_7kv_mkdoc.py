# -*- coding: utf-8 -*-
"""由 _7kv_judge.json 生成說明 markdown 主體。"""
import os, json
from collections import Counter, OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
J = json.load(open(os.path.join(HERE, "_7kv_judge.json"), encoding="utf-8"))
OUT = os.path.join(HERE, "說明_7K_01卷中之二.md")

# 檔 → chunk 對照（依 校閱 材料）
FILES = {}
for r in J:
    FILES.setdefault(r["f"], set()).add(r["seg"])
CHUNK = {}
for n in range(172, 201):
    CHUNK[n] = "06a" if n <= 183 else ("06b" if n <= 197 else "06c")

order = sorted(set(r["f"] for r in J))
lines = []
hdr = """# 7K 卷派工說明（01_行事鈔 卷中之二）

## 一、範圍與做法

- 派工清單：`AI語譯/_work/review/卷派工/01_行事鈔_卷中之二.tsv`（檔 172–206，共 35 檔）。
- 意見來源：`batch_qwen/r7k/resp_NNN.txt`（35 檔皆在）；`待跑_審查擋掉7K/回覆/` 無本卷檔。
- 對照材料：`校閱_7K/校閱_NNN.txt`（【原文】【譯文】）與 `AI語譯/out/01_行事鈔/06a|06b|06c_卷中之二.txt`。
- 逐段比對結果：本卷 74 段材料的【譯文】與 `out` 現行文**完全一致**，即本卷在發材料後未被其他輪次改動，無「已修」情形。
- 備份：`歸檔/7K卷修正前/01_行事鈔/06a_卷中之二_v.txt`、`06b_…_v.txt`、`06c_…_v.txt`（改動前原檔）。
- 行尾：06a 為 CRLF，06b／06c 為 LF，寫檔均保留。
- 未跑 `build_dirty`；只動本卷三個 chunk。
- chunk 對應：172–183 → `06a`（#2–#21）；184–197 → `06b`（#1–#35）；197–200 → `06c`（#1–#6）。

## 二、判定原則

- **改**：術語誤讀、義理譯反、語意牴觸、增譯致誤、主語歧義、明顯誤字。
- **否決**：潤飾、加註、體例（含全書「引號內句號」慣例）、原譯已達意、以及審閱者自身誤讀（多處已用《資持記》原文覆核）。
- **存疑**：涉及異解、校勘或文義難定者，不改字，另見 `存疑材料/7K_存疑.md`「01_行事鈔 卷中之二」節。

## 三、總表

| 檔 | chunk | 意見數 | 改 | 否決 | 存疑 |
|---|---|---|---|---|---|
"""
per = OrderedDict()
for r in J:
    per.setdefault(r["f"], []).append(r)
tot = Counter()
rows = []
for f in order:
    c = Counter(x["v"] for x in per[f])
    tot.update(c)
    rows.append("| %d | %s | %d | %d | %d | %d |" % (
        f, CHUNK.get(f, "?"), len(per[f]), c.get("改", 0), c.get("否決", 0), c.get("存疑", 0)))
lines.append(hdr + "\n".join(rows) + "\n| **計** |  | **%d** | **%d** | **%d** | **%d** |\n" % (
    len(J), tot["改"], tot["否決"], tot["存疑"]))

lines.append("""
## 四、逐檔明細

> 每條依「意見要點 → 判定（理由）」排列；「改」者均已套用並經驗證。

""")
for f in order:
    lines.append("### 檔 %d（%s）\n" % (f, CHUNK.get(f, "?")))
    for i, r in enumerate(per[f], 1):
        lines.append("%d. %s（#%d）**%s** — %s" % (i, r["pt"], r["seg"], r["v"], r["n"]))
    lines.append("")

open(OUT, "w", encoding="utf-8").write("\n".join(lines))
print("wrote", OUT, len(lines), "lines")
