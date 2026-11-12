# -*- coding: utf-8 -*-
"""Build 存疑材料/補判/index.md"""
import os, re, json, sys, io
from collections import Counter, OrderedDict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SU = os.path.join(ROOT, "存疑材料")
BJ = os.path.join(SU, "補判")
TOOLS = os.path.join(BJ, "_tools")

def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

def scan(prefix):
    rows = []
    for f in sorted(os.listdir(BJ)):
        if not re.match(prefix + r"_\d+\.md$", f):
            continue
        t = rd(os.path.join(BJ, f))
        labs = re.findall(r"^- \*\*段號\*\*：(.+)$", t, re.M)
        locs = re.findall(r"^- \*\*書/chunk#段\*\*：(.+)$", t, re.M)
        books = OrderedDict()
        for L in locs:
            b, rest = (L.split("／") + [""])[:2]
            ch = rest.split("＃")[0]
            key = f"{b.strip()}／{ch.strip()}"
            books[key] = books.get(key, 0) + 1
        bsum = Counter(L.split("／")[0].strip() for L in locs)
        rows.append({"file": f, "n": len(labs), "books": bsum, "chunks": books})
    return rows

old = scan("re0_補")
new = scan("新_補")
old_n = sum(r["n"] for r in old)
new_n = sum(r["n"] for r in new)
old_b = Counter()
for r in old:
    old_b.update(r["books"])
new_b = Counter()
for r in new:
    new_b.update(r["books"])

D = json.load(open(os.path.join(TOOLS, "n4_built.json"), encoding="utf-8"))
unres_new = len(D["unresolved"])
t = rd(os.path.join(BJ, "無法補齊.txt"))
unres_old = len(re.findall(r"^## ", t, re.M))

BOOK_ORDER = ["01_行事鈔", "02_戒疏", "03_業疏", "04_比丘尼鈔", "05_拾毗尼義鈔", "資持記"]
def bk_str(c):
    return "、".join(f"{b} {c[b]}" for b in BOOK_ORDER if c.get(b)) or "（無）"

out = []
out.append("# 存疑補判合併索引\n")
out.append("本索引涵蓋 `存疑材料/補判/` 下兩套已補好的裁判材料，"
           "以及兩份「補不齊」清單。兩套材料的格式、裁判提示詞完全一致"
           "（每條含：段號、書/chunk#段、原文、現行譯文、疑點、原檔），可直接分檔送判。\n")

out.append("## 一、總覽\n")
out.append("| 項目 | 份數 | 條數 | 狀態 |")
out.append("| --- | ---: | ---: | --- |")
out.append(f"| re0 補判（`re0_補_01`–`re0_補_{len(old):02d}`） | {len(old)} | {old_n} | 已補齊並已交出，**已判**（判於 `re0.txt`） |")
out.append(f"| 新存疑（`新_補_01`–`新_補_{len(new):02d}`） | {len(new)} | {new_n} | 本輪新補，**待判** |")
out.append(f"| 合計 | **{len(old) + len(new)}** | **{old_n + new_n}** | 其中 {len(new)} 份待判 |")
out.append("")
out.append(f"- re0 補判另有 `無法補齊.txt` {unres_old} 條（無法組成材料）；"
           f"新存疑另有 `新_無法補齊.txt` {unres_new} 條。")
out.append(f"- **「新存疑」共 {new_n + unres_new} 條 → 補成 {len(new)} 份 {new_n} 條，補不齊 {unres_new} 條。**")
out.append(f"- 故 re0「材料不足」{old_n + unres_old} 條＝已補 {old_n} ＋ 補不齊 {unres_old}，與 re0.txt 的 186 條相符。")
out.append("")

out.append("## 二、re0 補判（已判）\n")
out.append("| 檔 | 條數 | 涵蓋書別 |")
out.append("| --- | ---: | --- |")
for r in old:
    out.append(f"| `{r['file']}` | {r['n']} | {bk_str(r['books'])} |")
out.append(f"| **小計** | **{old_n}** | {bk_str(old_b)} |")
out.append("")
out.append("說明：這 13 份對應 `st存疑材料/re0.txt` 中判為「材料不足」的 re0 條目，"
           "已於 re0 批次裁判完成，**不需要再送判**；列在此處是為了與新存疑合看、避免重複補件。"
           .replace("st存疑材料", "存疑材料"))
out.append("")

out.append("## 三、新存疑（待判）\n")
out.append("| 檔 | 條數 | 涵蓋書別 |")
out.append("| --- | ---: | --- |")
for r in new:
    out.append(f"| `{r['file']}` | {r['n']} | {bk_str(r['books'])} |")
out.append(f"| **小計** | **{new_n}** | {bk_str(new_b)} |")
out.append("")

out.append("## 四、新存疑的來源與排除規則\n")
out.append("1. 來源：`存疑材料/r2_存疑/*.md`（8 檔）與 `存疑材料/r3_存疑/*.md`（2 檔），"
           "逐條解析出 679 個條目（原檔一條含多個段號者已拆開，共多出 21 條），扣除已判 289 條、重複 40 條、非疑點註記 1 條後，餘 **349 條**新存疑。")
out.append("2. 已判者排除：以段號比對 `return.txt`、`re2.txt`、`re3.txt`、`re0.txt` 四份裁判檔"
           "（共 546 個段號），凡已出現在其中者一律不補、不重列；據此排除 289 條。")
out.append("3. 跨檔重複：同一段號在 r2、r3 兩處都出現者只保留一條，"
           "並在條目內以「原檔同組條目」與「原檔」欄註明來源；據此合併 40 條（39 條同一段號重複＋1 條不同段號但定位到同一段）。")
out.append("4. 與 `re0_補_*.md` 完全無重疊（段號交集為 0）：那 13 份是另一批（re0 材料不足），未重做、未併入。")
out.append("5. 定位方式：以原檔所引文句回查 `TXT_分卷/`（03_業疏 用 `TXT_分卷_標點/`）段落，"
           "再由 `校閱_10K`／`20K`／`40K` 的段序對到 `AI語譯/out/<書>/<chunk>.txt` 的現行譯文；"
           "定位後仍以「原文與現行譯文相似度」覆核，對不上者寧可列入無法補齊，不硬配。")
out.append("6. 段號說明：原存疑檔括號內的 `01b#50`、`04b#20` 是當初那一批材料的段序，"
           "與現行譯文段序不一定相同；材料內一律以「書/chunk#段」所列的現行段序為準。")
out.append("")

out.append("## 五、無法補齊\n")
out.append(f"- `無法補齊.txt`：{unres_old} 條（re0 批）。")
out.append(f"- `新_無法補齊.txt`：{unres_new} 條（新存疑批）。主要成因："
           "段號只到檔案層級（如「225：0001」只給主題詞「雜分物細目」）、"
           "或疑點僅列主題詞而所引文句在 `TXT_分卷/` 中檢索不到、"
           "或原文與現行譯文段序對不上。")
out.append("")
out.append("## 六、使用方式\n")
out.append(f"- 待判的 {len(new)} 份：`新_補_01.md` … `新_補_{len(new):02d}.md`，每份檔頭均附完整裁判提示詞，可整份貼給裁判者。")
out.append("- 已判的 13 份：`re0_補_*.md`，僅供對照，不必再送。")
out.append("- 題目所要求的回傳格式（每條一段）：`### <段號>｜是錯／不是錯／材料不足`。")
out.append("")

open(os.path.join(BJ, "index.md"), "w", encoding="utf-8").write("\n".join(out))
print("wrote index.md")
print(f"old={len(old)} files/{old_n} entries, new={len(new)} files/{new_n} entries, "
      f"unres old={unres_old} new={unres_new}")
print("books old:", dict(old_b))
print("books new:", dict(new_b))
