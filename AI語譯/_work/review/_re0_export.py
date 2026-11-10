# -*- coding: utf-8 -*-
import json, io, os, collections
OUT = r"AI語譯/_work/review/_re0"
FIX = r"AI語譯/_work/review/fix_re0.tsv"
MIS = r"AI語譯/_work/review/re0_錯位.tsv"
MD  = r"AI語譯/_work/review/re0_說明.md"

rows = json.load(io.open(os.path.join(OUT, "rows.json"), encoding="utf-8"))
skips = json.load(io.open(os.path.join(OUT, "skips.json"), encoding="utf-8"))
mis = json.load(io.open(os.path.join(OUT, "mis.json"), encoding="utf-8"))
ents = json.load(io.open(os.path.join(OUT, "uniq2.json"), encoding="utf-8"))

# fix_re0.tsv
lines = []
for r in rows:
    t = r["new"]
    assert "\n" not in t and "\r" not in t and "\t" not in t, (r["book"], r["chunk"], r["seg"])
    lines.append("%s\t%s\t%d\t%s" % (r["book"], r["chunk"], r["seg"], t))
io.open(FIX, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")

# re0_錯位.tsv  gid\t書\tchunk\tseg\t建議\t理由
mlines = []
for gid, book, chunk, seg, sug, reason in sorted(mis, key=lambda x: x[0]):
    sug = (sug or "").replace("\t", " ").replace("\n", " ")
    reason = reason.replace("\t", " ")
    mlines.append("%s\t%s\t%s\t%d\t%s\t%s" % (gid, book, chunk, seg, sug, reason))
io.open(MIS, "w", encoding="utf-8", newline="\n").write("\n".join(mlines) + "\n")

# stats
book_counts = collections.Counter(r["book"] for r in rows)
# p-level by entries applied
prio = collections.Counter()
for e in ents:
    gid = e["gid"]
    dk = gid + "|" + e["type"]
    if any(gid == x[0] and e["seg"] == x[3] for x in skips):
        continue
for r in rows:
    pass
skip_reasons = collections.Counter()
for gid, book, chunk, seg, reason in skips:
    if "建議僅引" in reason: skip_reasons["建議不完整"] += 1
    elif "已見於次段" in reason or "已見於後文" in reason: skip_reasons["已由他段譯出"] += 1
    elif "不見於本段" in reason: skip_reasons["問題句不存在"] += 1
    else: skip_reasons["已修／已譯"] += 1

md = []
md.append("# re0 校閱修訂說明\n")
md.append("## 一、來源與數量\n")
md.append("- 來源檔：`校閱批次/new/已完成/re0/re0.txt`（231 條之申報數）。")
md.append("- 實際解析：檔案共 233 個 `###` 標題，其中 3 個為「存疑／存疑記錄」非意見條目；另有 2 條（044-0027、044-0053）漏失 `###` 前綴，已一併補解析。")
md.append("- 解析所得條目 232 條，其中 14 組為完全重複的貼上區塊（034、080、009 等批次重出），去重後**唯一意見 218 條**：01_行事鈔 118 條、02_戒疏 100 條。")
md.append("- 逐條比對現行 `AI語譯/out/<書>/<chunk>.txt` 後：")
md.append("  - **套用修訂：%d 條**，合併為 **%d 段**（同段多條已合併）。" % (len(json.load(io.open(os.path.join(OUT, "applied.json"), encoding="utf-8"))), len(rows)))
md.append("  - **跳過：28 條**（問題句已不在現行文字，或所指缺漏已由他段譯出，詳下）。")
md.append("  - **錯位：%d 條**（建議所改文字實屬他段，未套用，另列 `re0_錯位.tsv`）。" % len(mis))
md.append("")
md.append("## 二、輸出\n")
md.append("- `AI語譯/_work/review/fix_re0.tsv`：`book\\tchunk\\tseg\\tnew`，無表頭，共 %d 列。只改問題所指處，其餘逐字照抄現行段落。" % len(rows))
md.append("- `AI語譯/_work/review/re0_錯位.tsv`：`gid\\t書\\tchunk\\tseg\\t建議\\t理由`，共 %d 條。" % len(mis))
md.append("- 未寫入 `AI語譯/out/`，段落數不變，未加按語。")
md.append("")
md.append("## 三、統計\n")
md.append("| 項目 | 01_行事鈔 | 02_戒疏 | 合計 |")
md.append("|---|---:|---:|---:|")
md.append("| 唯一意見條數 | 118 | 100 | 218 |")
applied = json.load(io.open(os.path.join(OUT, "applied.json"), encoding="utf-8"))
ap = collections.Counter(a["book"] for a in applied)
md.append("| 套用條數 | %d | %d | %d |" % (ap.get("01_行事鈔",0), ap.get("02_戒疏",0), len(applied)))
md.append("| 產出段列 | %d | %d | %d |" % (book_counts.get("01_行事鈔",0), book_counts.get("02_戒疏",0), len(rows)))
md.append("| 跳過 | — | — | 28 |")
md.append("| 錯位 | — | — | %d |" % len(mis))
md.append("")
md.append("跳過原因分布：")
for k, v in skip_reasons.items():
    md.append("- %s：%d 條" % (k, v))
md.append("")
md.append("## 四、代表案例\n")
md.append("1. **001-0006（01_行事鈔/00_卷首#6，P1，意思相反）**：「闢重疑」之「闢」為破除，原譯作「開闢重大的疑義」。依《資持記》「闢遣皆去也」，將「誰能開闢重大的疑義、排遣通達的滯累」改為「誰能破除重重疑惑、排遣普遍的滯累妨難」，其餘全段照抄。")
md.append("2. **002-0003（01_行事鈔/01a_卷上之一#28，P1，因果或條件顛倒）**：原文「故勝也」本釋「殊勝」，譯文誤增「何以說是祕密？」並以殊勝之文置於祕密之下，因果自相矛盾。改為「何以說是殊勝？……所以最為殊勝。」")
md.append("3. **042-0025（01_行事鈔/12c_卷下之四#51，P0，漏譯或增譯）**：整段譯文誤貼為他段（二聖法通局）草稿，與本段《十誦律》受日法（七夜法、三十九夜法）全然無關；依建議整段改譯為受日法與羯磨文，段數不變。")
md.append("4. **004-0001（01_行事鈔/01b_卷上之一#61，P0，術語錯）→ 錯位**：建議所改「也通於僧人與別人這兩類人」實見於同卷 #64（004-0004）段，非本段 #61 文字，屬貼錯段，未套用，列 `re0_錯位.tsv`。")
md.append("5. **003-0063（01_行事鈔/01b_卷上之一#58，P0，漏譯或增譯）→ 跳過**：所指段末問答「問：別人之法，何名羯磨……」今已完整見於次段 #59 譯文；若再補入將重複，故跳過。")
md.append("")
md.append("## 五、處理原則\n")
md.append("- 以現行譯文為底，僅替換問題指出的字句；每筆替換均先驗證「待改字句在該段恰出現一次」，避免誤改他處。")
md.append("- 建議所引「原文」為文言、而現行譯文已白話化者，視為已修，不重複改寫（28 條跳過多屬此類）。")
md.append("- 建議所改字句在本段尋無、而見於同卷他段者，判為錯位，不套用、不代為搬移，另列供人工覆核。")
io.open(MD, "w", encoding="utf-8", newline="\n").write("\n".join(md) + "\n")

print("rows", len(rows), "mis", len(mis), "skips", len(skips))
print("fix chars", os.path.getsize(FIX))
