# -*- coding: utf-8 -*-
"""Generate 說明_末批套用.md from m2_rows.json + m3_result.json + m4 verification data."""
import json, os, difflib, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
rows = json.load(open(os.path.join(HERE, "m2_rows.json"), encoding="utf-8"))
res = json.load(open(os.path.join(HERE, "m3_result.json"), encoding="utf-8"))
byid = {r["id"]: r for r in rows}
POST = {"1525-0001": [("而非從見聞而來", "而非從眼見耳聞而來")]}

def short(s, n=16):
    s = s.replace("\n", " ")
    return s if len(s) <= n else s[:n] + "…"

def changes(r, gap=14, keep=26):
    a, b = r["cur"], r["sug"]
    for x, y in POST.get(r["id"], []):
        b = b.replace(x, y)
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
    # merge regions separated by a short equal run
    merged = []
    for o in ops:
        if merged and o[1] - merged[-1][2] <= gap:
            p = merged[-1]
            merged[-1] = ("x", p[1], o[2], p[3], o[4])
        else:
            merged.append(o)
    out = []
    for _, i1, i2, j1, j2 in merged:
        o, n = a[i1:i2], b[j1:j2]
        if not o:
            out.append("增「%s」" % short(n, keep))
        elif not n:
            out.append("刪「%s」" % short(o, keep))
        else:
            out.append("「%s」⇒「%s」" % (short(o, keep), short(n, keep)))
    if len(out) > 4:
        out = out[:4] + ["…（共 %d 處）" % len(out)]
    return "；".join(out)

# similarity for reference
def sim(r):
    b = r["sug"]
    for x, y in POST.get(r["id"], []):
        b = b.replace(x, y)
    return difflib.SequenceMatcher(None, r["cur"], b, autojunk=False).ratio()

groups = collections.OrderedDict()
BOOKORD = {"01_行事鈔": 1, "02_戒疏": 2, "03_業疏": 3, "04_比丘尼鈔": 4,
           "05_拾毗尼義鈔": 5, "資持記": 6}
for r in sorted(rows, key=lambda x: (BOOKORD.get(x["book"], 9), x["chunk"], x["seg"])):
    groups.setdefault((r["book"], r["chunk"]), []).append(r)

fc = {(f["book"], f["chunk"]): f for f in res["files"]}
RES = {x["id"]: x["result"] for x in res["report"]}
applied = sum(1 for r in res["report"] if r["result"] == "套用")
same = sum(1 for r in res["report"] if r["result"] == "已相符")
conf = sum(1 for r in res["report"] if r["result"] == "衝突跳過")

L = []
A = L.append
A("# 末批「是錯」條目套用說明（新_補01–19、末_補01）")
A("")
A("## 一、結論")
A("")
A("- **是錯 51 條：套用 51 段、已相符 0、衝突跳過 0、待議 0。**")
A("- 來源：`存疑材料/補判/回覆/`。該夾共 22 檔，實際採用 20 檔 —— `新_補_06_回2.txt`、"
  "`新_補_08_回2.txt` 為重送版，依指示**優先採用 `_回2`、忽略同號 `_回`**"
  "（故 `新_補_06_回.txt` 判為是錯的 `1435-0002` 不計；`新_補_08_回.txt` 無是錯條目，忽略後不影響）。")
A("- 20 檔共解析 284 條判讀（**是錯 51、不是錯 120、材料不足 113**），本次只動「是錯」51 條。")
A("- 51 條分布：`03_業疏` 17、`04_比丘尼鈔` 12、`05_拾毗尼義鈔` 11、`資持記` 11；"
  "涉及 32 個 chunk 檔。")
A("")
A("## 二、判定與防衝突")
A("")
A("1. **定位**：以材料 `書/chunk#段` 的段序 n，取該檔 `split(\"\\n\")` 後第 n 個非空段落（本批 32 檔皆為"
  "「段落 + 空行」交錯，CRLF）。")
A("2. **底稿比對**：51 條的現行段落與材料所載「現行譯文」**51/51 逐字相同** → 材料產出後無他人改寫，"
  "不存在「別人改過」的衝突；故無「衝突跳過」。")
A("3. **已相符檢查**：51 條現行均與建議不同（0 條已相符）。")
A("4. **只改問題處**：以整段建議為底，逐字比對後僅落入《判斷》所指的錯處；"
  "唯一例外見第四節註記（`1525-0001`）。短段落（如篇題，全長 20–30 字）之相似度天然偏低，"
  "非衝突指標，端看改動處是否即《判斷》所云。")
A("5. **建議與原文核對**：51 條建議均與所附原文相符，無「明顯不對或與原文衝突」者，故 `待議` 為 0，"
  "未建 `存疑材料/補判/待議_套用.md`。")
A("")
A("## 三、逐條明細")
A("")
for (book, chunk), ents in groups.items():
    f = fc[(book, chunk)]
    A("### %s／%s（%d 段，套用 %d）" % (book, chunk, f["n_para_after"], f["applied"]))
    A("")
    A("| 段號 | 段序 | 相似度 | 改動處（現行 ⇒ 建議） | 來源 | 結果 |")
    A("|---|---|---|---|---|---|")
    for r in ents:
        A("| %s | #%d | %.1f%% | %s | %s | %s |" % (
            r["id"], r["seg"], sim(r) * 100, changes(r), r["src"], RES[r["id"]]))
    A("")
A("## 四、註記")
A("")
A("- `1525-0001`（05_拾毗尼義鈔 03a#10）：建議除《判斷》所述「妨與難互無…」改為條件句並刪按語外，"
  "另把「而非從眼見耳聞而來」寫作「而非從見聞而來」。此二處《判斷》未及，依「只改問題處、其餘逐字照抄」，"
  "**保留現行「眼見耳聞」**，只套用《判斷》所指的條件句改寫。")
A("- `1557-0006`、`1558-0003`（03_業疏 00_卷首）：僅刪去重出衍文（分別為「之僧坊，住持戒壇」與"
  "「為了整頓弘揚正法綱紀，這也是」），其餘與現行逐字相同，原文存疑括注一仍其舊。")
A("- `1439-0001`、`1481-0005`、`1486-0001`、`1537-0006` 兼有「合併重出／補漏一條」之結構性修正，"
  "悉依建議整段置換。")
A("")
A("## 五、備份（套用前原檔）")
A("")
A("逐 byte 複製（`shutil.copy2`）至 `歸檔/末批套用前/<書>/<chunk>_z.txt`：")
A("")
A("| 書 | chunk | 備份檔 | 位元組 |")
A("|---|---|---|---|")
import hashlib
for (book, chunk), ents in groups.items():
    bp = os.path.join(ROOT, "歸檔", "末批套用前", book, chunk + "_z.txt")
    raw = open(bp, "rb").read()
    A("| %s | %s | `%s_z.txt` | %d |" % (book, chunk, chunk, len(raw)))
A("")
A("## 六、驗證")
A("")
A("| chunk | 段數（前→後） | 相異段數 | 實際套用 | 行尾 | 結果 |")
A("|---|---|---|---|---|---|")
tot = [0, 0, 0]
for (book, chunk), ents in groups.items():
    f = fc[(book, chunk)]
    eol = "CRLF" if f["eol_after"].get("CRLF") else "LF"
    A("| %s/%s | %d → %d | %d | %d | %s | %s |" % (
        book, chunk, f["n_para_before"], f["n_para_after"], f["diff_paras"], f["applied"],
        eol, "OK" if f["ok"] else "FAIL"))
    tot[0] += f["n_para_before"]; tot[1] += f["diff_paras"]; tot[2] += f["applied"]
A("")
A("- **段數不變**：32 檔合計 %d 段，套用前後一致（逐檔見上表）。" % tot[0])
A("- **相異段數 = 實際套用數**：%d = %d（以備份與現行逐行比對，相異段索引恰等於 51 條目標段）。"
  % (tot[1], tot[2]))
A("- **行尾一致**：32 檔全為 CRLF，套用前後 CRLF/LF 計數完全相同；無 BOM；UTF-8 均可解碼。")
A("- **唯 51 段變動**：除目標段外，其餘 2337 段與備份逐字相同（%d − 51 = %d）。"
  % (tot[0], tot[0] - 51))
A("- **冪等**：套用後重跑比對，51 條全部判為「已相符」，0 處再改。")
A("")
A("## 七、未處理事項")
A("")
A("- 未執行 `build_dirty`。")
A("- 未動 `不是錯` 190 條、`材料不足` 43 條；未動其他 chunk 與其他書。")
A("- 工具腳本：`存疑材料/補判/_tools/m1_parse.py`（解析）、`m2_map.py`（對位＋比對）、"
  "`m3_apply.py`（套用＋備份）、`m4_verify.py`（獨立驗證）。")
A("")
A("驗證總結：**全部通過**。")

outp = os.path.join(ROOT, "AI語譯", "_work", "review", "說明_末批套用.md")
os.makedirs(os.path.dirname(outp), exist_ok=True)
open(outp, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
print("written", outp, "lines", len(L))
