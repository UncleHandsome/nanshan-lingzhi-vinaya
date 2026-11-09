# -*- coding: utf-8 -*-
import json, io
rows = json.load(open(r"AI語譯\_work\review\_re4g1\rows.json", encoding="utf-8"))
lines = io.open(r"AI語譯\_work\review\fix_re4_g1.tsv", encoding="utf-8").read().rstrip("\n").split("\n")
new = {}
order = []
for ln in lines:
    p = ln.split("\t"); new[(p[1],p[2])] = p[3]; order.append((p[1],p[2]))
sel = [7,15,30,44,59,67,81,98,109,132,139,143,151,154,83,47,51]
for i in sel:
    r = rows[i-1]; k=(r["chunk"], r["seg"]); t = new[k]
    # find a distinctive anchor from the suggestion/new
    print("="*90)
    print("R%d %s/%s" % (i, r["chunk"], r["seg"]))
    if i == 7:
        j = t.find("六十五不可穿"); print(t[j:j+140])
    elif i == 83:
        j = t.find("這首詩"); print(t[max(0,j-60):j+160])
    elif i == 15:
        j = t.find("契會滅諦"); print(t[max(0,j-80):j+60])
    elif i == 30:
        j = t.find("修行的意義"); print(t[max(0,j-80):j+80])
    elif i == 44:
        j = t.find("泛泛提及"); print(t[max(0,j-80):j+60])
    elif i == 59:
        j = t.find("道含性"); print(t[max(0,j-80):j+60])
    elif i == 67:
        j = t.find("聚眾大眾"); print(t[max(0,j-90):j+60])
    elif i == 81:
        j = t.find("斬斷首級"); print(t[max(0,j-90):j+60])
    elif i == 98:
        j = t.find("以會通此處"); print(t[max(0,j-100):j+120])
    elif i == 109:
        j = t.find("逼臨門戶"); print(t[max(0,j-80):j+60])
    elif i == 132:
        j = t.find("說戒布薩"); print(t[max(0,j-80):j+60])
    elif i == 139:
        j = t.find("應當結治"); print(t[max(0,j-60):j+100])
    elif i == 143:
        j = t.find("這兩者行懺"); print(t[max(0,j-100):j+60])
    elif i == 151:
        j = t.find("治覆羯磨"); print(t[max(0,j-80):j+60])
    elif i == 154:
        j = t.find("和合僧眾"); print(t[max(0,j-80):j+60])
    elif i == 47:
        j = t.find("入定之處"); print(t[max(0,j-60):j+220])
    elif i == 51:
        j = t.find("苦集二諦"); print(t[max(0,j-60):j+240])
