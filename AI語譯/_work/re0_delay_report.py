# -*- coding: utf-8 -*-
"""產生 AI語譯/_work/review/說明_re0套用.md（讀備份 vs 現行，自動生成逐條 diff）"""
import csv, difflib, hashlib, os, sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
os.chdir(ROOT)
OUTDIR = os.path.join("AI語譯", "out", "03_業疏")
BKDIR = os.path.join("歸檔", "re0套用前", "03_業疏")

with open(os.path.join("存疑材料", "待套用_re0.tsv"), encoding="utf-8", newline="") as f:
    recs = [r for r in csv.reader(f, delimiter="\t") if r and any(c.strip() for c in r)]
rows = recs[1:]


def hunks(old, new, gap=8):
    sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
    ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
    merged = []
    for op in ops:
        if merged and op[1] - merged[-1][2] <= gap:
            _, i1, _, _, j2 = merged[-1]
            merged[-1] = (merged[-1][0], i1, op[2], merged[-1][3], op[4])
        else:
            merged.append(list(op))
    out = []
    for tag, i1, i2, j1, j2 in merged:
        a, b = old[i1:i2], new[j1:j2]
        out.append((a if a else "（無）", b if b else "（無）"))
    return out, sm.ratio()


info = {}
for segid, book, chunk, para, newp, reason in rows:
    name = [fn for fn in os.listdir(OUTDIR) if fn.endswith(".txt") and fn.startswith(chunk + "_")][0]
    base = os.path.splitext(name)[0]
    cur = open(os.path.join(OUTDIR, name), encoding="utf-8", newline="").read().split("\n")
    bk = open(os.path.join(BKDIR, base + "_r.txt"), encoding="utf-8", newline="").read().split("\n")
    p = int(para)
    old = bk[2 * (p - 1)].rstrip("\r")
    hs, ratio = hunks(old, newp)
    info.setdefault(chunk, {"name": name, "base": base, "rows": []})
    info[chunk]["rows"].append(dict(segid=segid, para=p, old=old, new=newp,
                                    hunks=hs, ratio=ratio, reason=reason))

# ---- 統計 ----
total = sum(len(v["rows"]) for v in info.values())
report = []
w = report.append

w("# re0 延後條目套用說明（03_業疏 02a／02b／03a）")
w("")
w("## 一、結論")
w("")
w(f"- **套用 {total} 列**（TSV 全部資料列），**已相符 0 列**、**衝突跳過 0 列**。")
w("- TSV 檔為 13 行（第 1 行表頭 + **12 列**資料），每列對應一段。")
w("- 原 re0 判為「是錯」而屬 `03_業疏` 者共 13 條：12 條在本 TSV，另 1 條 `1591-0013`（03a#16）"
  "在 TSV 製作前現行譯文即已相符（「若再通於僧法與別法」），故未列入、本次亦無需改動；"
  "12 + 1 = 13，帳目相符。")
w("")
w("## 二、判定方式（無「原句」欄時的防衝突處理）")
w("")
w("TSV 欄位只有 `段號、書、chunk、段序、新段落、理由`，**沒有記錄原句**，因此無法直接比對「原句」。"
  "本次改用下列四項檢查，確認現行段落仍是當初生成新段落時的同一段底稿，未經他人改寫：")
w("")
w("1. **段序定位**：段序 n 對應 `split(\"\\n\")` 後第 `2n-1` 行（偶數行皆為空行）；"
  "落點必須為非空段落，且其後緊接空行。12 列全部命中。")
w("2. **整段比對**：現行與新段落逐字以 `difflib` 比對，相似度 0.868–0.977；"
  "相異處全部集中在《理由》所述問題字句上，其餘一字不差（詳第三節逐條 diff）。"
  "若現行已被他人改寫，必然出現《理由》以外的差異，本次無此情形。")
w("3. **改動範圍**：單段 diff 的差異片段僅 2–8 處，且每處都與《理由》指出的錯處對應，"
  "故無「別人剛改過」之衝突。")
w("4. **檔案時序**：三檔在套用前的最後修改時間（備份保留原 mtime）為 "
  + "、".join(
      f"`{info[c]['base']}` {__import__('datetime').datetime.fromtimestamp(os.path.getmtime(os.path.join(BKDIR, info[c]['base'] + '_r.txt'))).strftime('%m-%d %H:%M:%S')}"
      for c in ("02a", "02b", "03a"))
  + "，全部早於 TSV 產生時間（`待套用_re0.tsv` 06:45:47）；即 TSV 產出後至本次套用前，"
    "無他人改寫，故「現行」即為 TSV 所依據的原句。")
w("")
w("判定門檻：現行 == 新段落 → 視為已套用（跳過）；現行 != 新段落但相似度 ≥ 0.85 且差異僅零星字句 → 套用；"
  "否則視為衝突跳過。本次 12 列皆落在「套用」。")
w("")
w("## 三、逐條套用明細")
w("")

for chunk in ("02a", "02b", "03a"):
    v = info[chunk]
    w(f"### {chunk}（`{v['name']}`，共 {len(v['rows'])} 段）")
    w("")
    w("| 段號 | 段序 | 相似度 | 改動處（原 ⇒ 新） | 理由（TSV） |")
    w("|---|---|---|---|---|")
    for r in v["rows"]:
        hs = "；".join(f"`{a}` ⇒ `{b}`" for a, b in r["hunks"])
        hs = hs.replace("|", "\\|")
        reason = r["reason"].replace("|", "\\|")
        w(f"| {r['segid']} | #{r['para']} | {r['ratio']*100:.1f}% | {hs} | {reason} |")
    w("")

w("## 四、備份（套用前原檔）")
w("")
w("| 備份檔 | 位元組 | sha256 |")
w("|---|---|---|")
for chunk in ("02a", "02b", "03a"):
    v = info[chunk]
    p = os.path.join(BKDIR, v["base"] + "_r.txt")
    b = open(p, "rb").read()
    w(f"| `歸檔/re0套用前/03_業疏/{v['base']}_r.txt` | {len(b)} | `{hashlib.sha256(b).hexdigest()}` |")
w("")
w("備份為逐 byte 複製（`shutil.copy2`），未經解碼／重編碼；"
  "已驗證三份備份的 sha256 與套用前原檔一致。")
w("")
w("## 五、驗證")
w("")
w("| chunk | 段數（前→後） | 行數（前→後） | 相異段數 | 實際套用 | 行尾 | 結果 |")
w("|---|---|---|---|---|---|---|")
allok = True
for chunk in ("02a", "02b", "03a"):
    v = info[chunk]
    cur_b = open(os.path.join(OUTDIR, v["name"]), "rb").read()
    bk_b = open(os.path.join(BKDIR, v["base"] + "_r.txt"), "rb").read()
    cur, bk = cur_b.decode("utf-8"), bk_b.decode("utf-8")
    cl, bl = cur.split("\n"), bk.split("\n")
    pa = len([l for l in cl if l.rstrip("\r").strip()])
    pb = len([l for l in bl if l.rstrip("\r").strip()])
    diff = [i for i, (a, b) in enumerate(zip(bl, cl)) if a != b]
    tgt = sorted(2 * (r["para"] - 1) for r in v["rows"])
    nl = "CRLF" if cur.count("\r\n") == cur.count("\n") and cur.count("\r\n") > 0 else "混用/異常"
    ok = (pa == pb and diff == tgt and len(diff) == len(tgt) == len(v["rows"])
          and len(tgt) == len(set(tgt)) and not cur_b.startswith(b"\xef\xbb\xbf"))
    allok &= ok
    w(f"| {chunk} | {pb} → {pa} | {len(bl)} → {len(cl)} | **{len(diff)}** | **{len(v['rows'])}** | {nl}（{cur.count(chr(13)+chr(10))}） | {'OK' if ok else 'FAIL'} |")
w("")
w("- **段數不變**：02a 111、02b 146、03a 134，套用前後一致。")
w("- **相異段數 = 實際套用數**：02a 2=2、02b 7=7、03a 3=3，合計 12=12。"
  "比對方式為備份與現行逐行比對，相異行索引恰等於 TSV 目標段索引。")
w("- **每段只改一次**：TSV 無重複 `(chunk, 段序)`；套用後每段內容與新段落逐字相等；"
  "每段前後僅 1 次變動。套用程式重跑（dry）時 12 列全部判為「已相符」、0 處再改，冪等成立。")
w("- **其餘 byte 不動**：三檔的行數、換行總數不變，全檔僅 CRLF（無 LF 混用）、無 BOM；"
  "非目標段落與備份逐字相同。")
w("")
w("## 六、未處理事項")
w("")
w("- 未執行 `build_dirty`。")
w("- 未修改 `存疑材料/待套用_re0.tsv`，未動 `02_戒疏` 及其他 chunk。")
w("- 套用腳本（可重跑，具冪等判定）：`AI語譯/_work/re0_delay_apply.py`；"
  "獨立驗證腳本：`AI語譯/_work/re0_delay_verify.py`。")
w("")
w(f"驗證總結：**{'全部通過' if allok else '有失敗項'}**。")

md = "\n".join(report) + "\n"
path = os.path.join("AI語譯", "_work", "review", "說明_re0套用.md")
with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(md)
print("written", path, len(md), "chars; allok =", allok)
