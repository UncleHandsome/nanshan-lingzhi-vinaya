# -*- coding: utf-8 -*-
"""Part 2 (v2): rebuild 裁判材料 for the 186 材料不足 items."""
import os, re, json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SU = os.path.join(ROOT, "存疑材料")
TOOLS = os.path.join(SU, "補判", "_tools")
BJ = os.path.join(SU, "補判")

rows = json.load(open(os.path.join(TOOLS, "resolved4.json"), encoding="utf-8"))

def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

def kj_src(num, code):
    t = rd(os.path.join(ROOT, "校閱_10K", f"校閱_{num}.txt"))
    head = re.search(r"^【%s】(.*)$" % re.escape(code), t, re.M)
    if not head:
        return "", ""
    rest = t[head.end():]
    m2 = re.search(r"\n【譯文】", rest)
    src = rest[:m2.start()] if m2 else rest
    return head.group(1).strip(), re.sub(r"^【原文】", "", src.strip())

OV = {"327-0001": ("02_戒疏", "01c", 41), "337-0004": ("02_戒疏", "01d", 94)}
MANUAL = {
    "327-0001": ("r3_存疑/02_戒疏.md",
                 "327：0001 記文同釋此五刑，「割」亦作「削去耳朵」，與 326 同一存疑；「奏法→秦法」校注體例未統一。"),
    "337-0004": ("r3_存疑/02_戒疏.md",
                 "337：0004「縱是佛說…豈妄承奉」與 0005 記文「雖非究竟，義須承奉」正反兩讀（承奉與否），現譯一從記文，未改。"),
}

for r in rows:
    if r["key"] in OV:
        book, chunk, seg = OV[r["key"]]
        _, src = kj_src(r["key"].split("-")[0], r["key"])
        d = os.path.join(ROOT, "AI語譯", "out", book)
        fn = sorted(f for f in os.listdir(d) if f.startswith(chunk) and f.endswith(".txt"))[0]
        ps = [l for l in rd(os.path.join(d, fn)).split("\n") if l.strip()]
        r.update({"book": book, "chunk": chunk, "seg": seg, "src": src, "cur": ps[seg - 1]})
    if r["key"] in MANUAL:
        r["srcfile"], r["su_note"] = MANUAL[r["key"]]

def one_line(s):
    s = re.sub(r"\s*\n\s*", "　", s.strip())
    return s

def clean_note(raw):
    s = raw.strip()
    s = re.sub(r"^\*\*", "", s)
    s = re.sub(r"^\d+\.\s*", "", s)
    s = s.replace("**", "")
    s = re.sub(r"：\s*", "：", s, count=1)
    return one_line(s)

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

good = [r for r in rows if r["src"].strip() and r["cur"].strip()]
bad = [r for r in rows if not (r["src"].strip() and r["cur"].strip())]
PER = 12
files = [good[i:i + PER] for i in range(0, len(good), PER)]

# clear old
for f in os.listdir(BJ):
    if re.match(r"re0_補_\d+\.md$", f):
        os.remove(os.path.join(BJ, f))

for fi, group in enumerate(files, 1):
    out = [f"# 存疑裁判材料：re0 補判 第 {fi:02d} 份（共 {len(files):02d} 份）\n",
           "## 裁判提示詞（全文）\n",
           "```text\n" + PROMPT + "\n```\n",
           "## 材料開始\n"]
    for r in group:
        out.append(f"### {r['key']}\n")
        out.append(f"- **段號**：{r['key']}")
        out.append(f"- **書/chunk#段**：{r['book']}／{r['chunk']}＃{r['seg']}")
        out.append(f"- **原文**：{re.sub(r'^【原文】', '', r['src'].strip())}")
        out.append(f"- **現行譯文**：{r['cur'].strip()}")
        out.append(f"- **疑點**：{clean_note(r['su_note'])}")
        out.append(f"- **原檔**：{r['srcfile']}\n")
    open(os.path.join(BJ, f"re0_補_{fi:02d}.md"), "w", encoding="utf-8").write("\n".join(out))

out = ["# 無法補齊清單（re0 材料不足 186 條中，原始存疑檔亦缺完整資訊者）", "",
       "說明：以下各條回到 `存疑材料/r2_存疑/*.md`、`r3_存疑/*.md` 後，原始紀錄仍只有標題詞或一句主題，",
       "沒有原文或譯文，無法組成裁判材料。列出段號、所屬書、原檔位置與現有材料，供另行補查。", ""]
for r in bad:
    out.append(f"## {r['key']}")
    out.append(f"- **書**：{r['book'] or '未定'}")
    out.append(f"- **原檔**：{r['srcfile'] or '未定位'}")
    out.append(f"- **原檔現有內容**：{clean_note(r.get('su_note', '')) or '（無）'}")
    miss = []
    if not r["src"].strip(): miss.append("原文")
    if not r["cur"].strip(): miss.append("譯文")
    if not (r["chunk"] and r["seg"]): miss.append("chunk#段（段號不足以定位）")
    out.append(f"- **缺**：{'、'.join(miss)}")
    out.append("")
open(os.path.join(BJ, "無法補齊.txt"), "w", encoding="utf-8").write("\n".join(out))
print("good", len(good), "bad", len(bad), "files", len(files))
