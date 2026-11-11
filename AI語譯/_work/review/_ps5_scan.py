# -*- coding: utf-8 -*-
"""在資持記 01a-02a（r2 已處理範圍）掃描：重複贅字、現代詞、常見語病。"""
import re, os, glob, json

BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(BASE, "AI語譯", "out", "資持記")
FILES = ["01a", "01b", "01c", "01d", "01e", "01f", "02a"]

paras = []
for p in sorted(glob.glob(os.path.join(OUT, "*.txt"))):
    base = os.path.basename(p)
    if not any(base.startswith(f) for f in FILES):
        continue
    chunk = os.path.splitext(base)[0]
    idx = 0
    for ln in open(p, encoding="utf-8").read().split("\n"):
        if ln.strip():
            idx += 1
            paras.append((chunk, idx, ln.strip()))

print("paras:", len(paras))

# 1) 同段內重複的二字詞（相距 < 12 字）
dup = []
for chunk, idx, t in paras:
    i = 0
    seen = []
    for m in re.finditer(r"[\u4e00-\u9fff]{2,4}", t):
        s = m.group(0)
        if len(s) < 2:
            continue
    # 以固定窗掃相鄰二字
    grams = {}
    for i in range(len(t) - 1):
        g = t[i:i+2]
        if not re.match(r"^[\u4e00-\u9fff]{2}$", g):
            continue
        grams.setdefault(g, []).append(i)
    for g, pos in grams.items():
        if len(pos) < 2:
            continue
        for a, b in zip(pos, pos[1:]):
            if 2 <= b - a <= 8:
                ctx = t[max(0, a-14):min(len(t), b+16)]
                dup.append((chunk, idx, g, ctx))
                break

uniq = {}
for chunk, idx, g, ctx in dup:
    key = (chunk, idx, g)
    if key not in uniq:
        uniq[key] = ctx
print("dup bigram cases:", len(uniq))
with open(os.path.join(BASE, "AI語譯", "_work", "review", "_dup.txt"), "w", encoding="utf-8") as f:
    for (chunk, idx, g), ctx in sorted(uniq.items()):
        f.write("%s#%d [%s] %s\n" % (chunk.split("_")[0], idx, g, ctx))

MODERN = ["考評", "局處", "免職", "機制", "層面", "系統", "平台", "項目", "團隊", "指標",
          "評估", "審核", "考核", "落實", "把關", "打造", "梳理", "邏輯", "維度", "框架",
          "格局", "路徑", "模组", "模組", "運營", "成本", "效益", "水平", "底線", "節點",
          "環節", "流程", "渠道", "資源", "資訊", "數據", "檔案", "模範", "對象", "客體",
          "主體", "成分", "條件", "性質", "原則", "方式", "過程", "現象", "本質", "規律",
          "意識", "觀念", "思維", "內容", "形式", "結構", "功能", "作用", "效果", "目的",
          "手段", "措施", "方案", "政策", "制度", "組織", "管理", "控制", "操作", "執行",
          "實施", "推動", "促進", "提升", "優化", "整合", "協調", "溝通", "反饋", "開放",
          "封閉", "正面", "負面", "客觀", "主觀", "具體", "抽象", "積極", "消極", "強度"]
hits = []
for chunk, idx, t in paras:
    for w in MODERN:
        if w in t:
            i = t.index(w)
            hits.append((w, chunk, idx, t[max(0, i-20):i+len(w)+20]))
print("modern hits:", len(hits))
with open(os.path.join(BASE, "AI語譯", "_work", "review", "_modern.txt"), "w", encoding="utf-8") as f:
    for w, chunk, idx, ctx in sorted(hits):
        f.write("%s  %s#%d  %s\n" % (w, chunk.split("_")[0], idx, ctx))
