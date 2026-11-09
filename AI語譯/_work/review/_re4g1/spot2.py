# -*- coding: utf-8 -*-
import json, io
rows = json.load(open(r"AI語譯\_work\review\_re4g1\rows.json", encoding="utf-8"))
lines = io.open(r"AI語譯\_work\review\fix_re4_g1.tsv", encoding="utf-8").read().rstrip("\n").split("\n")
new = {}
for ln in lines:
    p = ln.split("\t"); new[(p[1],p[2])] = p[3]
sel = {10:"私情揣度",11:"篇幅僅有一卷",12:"本師佛陀",62:"同樣通於勸信",70:"並非單取外在形相",72:"感念三寶",84:"「山」字下方",85:"半月分為黑月",86:"見、聞、疑",96:"三遍與一遍",100:"不配屬於前段",101:"二持與二犯",105:"使者尼僧",107:"若本處無人能誦",114:"持戒與犯戒兩類",116:"「止善」",117:"自「乘」字以下",124:"現在疏中說",125:"唯恐病情加重",141:"僧眾全體共同違犯",144:"不用以口頭呈報",145:"白二、白四",148:"屏處坐戒",149:"不合聽戒",150:"詣官告人",156:"在「一切」以下",157:"後一首偈頌"}
for i, anchor in sel.items():
    r = rows[i-1]; k=(r["chunk"], r["seg"]); t = new.get(k)
    if t is None: print("MISSING", i); continue
    j = t.find(anchor)
    print("="*90); print("R%d %s/%s" % (i, r["chunk"], r["seg"]))
    if j < 0:
        print("ANCHOR NOT FOUND:", anchor, "||", t[:120])
    else:
        print(t[max(0,j-100):j+130])
