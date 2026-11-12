# -*- coding: utf-8 -*-
"""Write 新_補_NN.md + 新_無法補齊.txt + index.md."""
import os, re, json, sys, io, math
from collections import Counter, OrderedDict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SU = os.path.join(ROOT, "存疑材料")
BJ = os.path.join(SU, "補判")
TOOLS = os.path.join(BJ, "_tools")

D = json.load(open(os.path.join(TOOLS, "n4_built.json"), encoding="utf-8"))
R, U = D["resolved"], D["unresolved"]

PROMPT = """你是南山律典譯文的資深校勘者。下面每條有一個「疑點」，是前一位校閱者不確定、暫時擱下的問題。

請對每一條給出明確結論，不要含糊：
1. 讀原文與譯文，判斷疑點成立不成立。
2. 結論只有三種：
   - 是錯：指出錯在哪，並給整段替換文字。
   - 不是錯：說明為什麼原文支持現行譯法。
   - 材料不足：指出缺什麼，不要猜。

輸出格式（每條一段）：
### <段號>｜是錯
判斷：…
建議：（整段替換文字，其餘與現譯逐字相同）

### <段號>｜不是錯
判斷：…

### <段號>｜材料不足
判斷：需查…，現有材料無法判定。

規則：
- 「是錯」才給建議，且必須是完整段落。
- 不要硬判；材料不足就寫材料不足。
- 不要改原文、不要合併段落、不要加譯者按語。"""

nkey = lambda s: re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", s)
BOOK_ORDER = ["01_行事鈔", "02_戒疏", "03_業疏", "04_比丘尼鈔", "05_拾毗尼義鈔", "資持記"]

def clean(txt):
    t = txt.replace("**", "")
    t = re.sub(r"`", "", t)
    t = re.sub(r"\s*\n\s*", "　", t)
    t = re.sub(r"\u3000{2,}", "　", t)
    t = re.sub(r"[ \t]{2,}", " ", t)
    t = re.sub(r"^[　\s]+|[　\s]+$", "", t)
    return t

def note_text(r):
    src_key = nkey(r["src"])
    parts = []
    for n in r["notes"]:
        head = clean(n["raw"])
        body = clean(n["body"])
        t = head
        if body and body not in head:
            t += "　——　" + body
        qs = [nkey(q) for q in re.findall(r"「([^」]{3,24})」", n["raw"])]
        qs = [q for q in qs if len(q) >= 3]
        if qs and not any(q in src_key for q in qs):
            t += "〔此條所引文句未見於上列原文，恐係同段另一處，請斟酌〕"
        if t not in parts:
            parts.append(t)
    s = "　∥　".join(parts)
    s = re.sub(r"(∥　){2,}", "∥　", s)
    if r.get("siblings"):
        s += f"（原檔同組條目：{'、'.join(r['siblings'])}）"
    return s

def loc_label(r):
    return f"{r['book']}／{r['chunk']}＃{r['seg']}"

R.sort(key=lambda r: (BOOK_ORDER.index(r["book"]) if r["book"] in BOOK_ORDER else 9,
                      r["chunk"], r["seg"], r["label"]))
N = len(R)
PER = 14
nfiles = max(1, math.ceil(N / PER))
base, extra = divmod(N, nfiles)
sizes = [base + (1 if i < extra else 0) for i in range(nfiles)]
print("entries", N, "files", nfiles, "sizes", sizes)

if os.path.exists(os.path.join(BJ, "新_補_01.md")):
    for f in os.listdir(BJ):
        if re.match(r"新_補_\d+\.md$", f):
            os.remove(os.path.join(BJ, f))

idx = 0
manifest = []
for fi, sz in enumerate(sizes, 1):
    group = R[idx:idx + sz]
    idx += sz
    books = OrderedDict()
    for r in group:
        books[r["book"]] = books.get(r["book"], 0) + 1
    out = []
    out.append(f"# 存疑裁判材料：新存疑 第 {fi:02d} 份（共 {nfiles:02d} 份，本份 {len(group)} 條）\n")
    out.append("## 裁判提示詞（全文）\n")
    out.append("```text\n" + PROMPT + "\n```\n")
    out.append("## 材料說明\n")
    out.append("- 本份涵蓋：" + "、".join(f"{b} {n} 條" for b, n in books.items()) + "。")
    out.append("- 這些條目出自 `存疑材料/r2_存疑/*.md`、`r3_存疑/*.md`，"
               "段號與疑點均未見於 `return.txt`、`re2.txt`、`re3.txt`、`re0.txt` 四份裁判檔，"
               "即尚未判過；`re0_補_*.md` 已補过的 186 條不在此列。")
    out.append("- 「段號」沿用原存疑檔的編號；「書/chunk#段」與「原文」以 `TXT_分卷/`"
               "（03_業疏 用 `TXT_分卷_標點/`）的段落為準；「現行譯文」取自 "
               "`AI語譯/out/<書>/<chunk>.txt` 目前對應段落。")
    out.append("- 原存疑檔括號內的 `01b#50`、`04b#20` 之類標記，是當時那一批材料的段序，"
               "與現行譯文的段序**不一定相同**；本材料一律以「書/chunk#段」所列的現行段序為準。")
    out.append("- 「疑點」逐字錄自原始存疑檔（僅去 Markdown 星號與反引號），"
               "若原檔一條含多個段號，會標明「原檔同組條目」。")
    out.append("- 少數條目原檔只給主題詞、沒有可檢索的引文，是以原檔段號對位（未經引文覆核）；"
               "若發現該條原文與疑點所說明顯不合，請逕判「材料不足」，不要勉強判定。\n")
    out.append("## 材料開始\n")
    for r in group:
        out.append(f"### {r['label']}\n")
        out.append(f"- **段號**：{r['label']}")
        out.append(f"- **書/chunk#段**：{loc_label(r)}")
        out.append(f"- **原文**：{r['src'].strip()}")
        out.append(f"- **現行譯文**：{r['tra'].strip()}")
        out.append(f"- **疑點**：{note_text(r)}")
        out.append(f"- **原檔**：{'；'.join(sorted(set(r['srcs'])))}\n")
    p = os.path.join(BJ, f"新_補_{fi:02d}.md")
    open(p, "w", encoding="utf-8").write("\n".join(out))
    manifest.append({"file": f"新_補_{fi:02d}.md", "n": len(group),
                     "books": dict(books)})
    print("wrote", p, len(group))

# ---------- 新_無法補齊 ----------
out = ["# 新存疑無法補齊清單", "",
       "說明：以下條目出自 `存疑材料/r2_存疑/*.md`、`r3_存疑/*.md`，"
       "但段號只到檔案層級（如「225：0001」無對應段落），或疑點僅有主題詞、"
       "所引文句在 `TXT_分卷/` 中檢索不到，無法組成可判的完整材料。",
       "列出段號、原檔位置、現有內容與缺什麼，供另行補查。", ""]
U.sort(key=lambda u: (u["src"], u["raw"]))
for u in U:
    out.append(f"## {u['raw'][:80] or '（無標題）'}")
    out.append(f"- **原檔**：{u['src']}")
    out.append(f"- **原檔現有內容**：{clean(u['raw'] + '　' + u['body'])[:400]}")
    if u.get("terms"):
        out.append(f"- **檢索詞**：{'、'.join(u['terms'])}")
    if u.get("files"):
        out.append(f"- **檔案層級段號**：{'、'.join(u['files'])}")
    out.append(f"- **缺**：{u['reason']}")
    out.append("")
open(os.path.join(BJ, "新_無法補齊.txt"), "w", encoding="utf-8").write("\n".join(out))
print("wrote 新_無法補齊.txt", len(U))
json.dump(manifest, open(os.path.join(TOOLS, "manifest_new.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
