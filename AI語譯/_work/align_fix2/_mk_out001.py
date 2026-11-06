# -*- coding: utf-8 -*-
"""Build out_001.json for align_fix2 batch 001 (sec 26 瞻病送終).

Mapping derived from 牒詞 + 義理順序:
  c0 就中即二…四位        <- z0  篇題（瞻病/送終兩門）+ 制意初科起
  c1 制意者…              <- z1 瞻視/凡情/彰聖引導 ; z2 律緣/立制/結勸/問答
  c2 二簡人中…            <- z3 簡人(親屬/僧與/僧差/女眾) ; z4 無乘往求/尼眾/下眾
  c3 次明供給法…          <- z5 五百問/寶梁/九橫 ; z6 己物→僧物→乞與/五德 ; z7 十誦/善生/五百問 ; z8 伽論/便器(安置科起)
  c4 三安置處所…          <- z9 本傳/無常院 ; z10 立彌陀/西方 ; z11 像向西/忍土/臭穢 ; z12 諸天衛護/恒在佛所
  c5 四說法勸善者…        <- z12 四中初科/深法/是道非道
  c6 若阿練若者…          <- z13 捨座捨衣/誦經鸚鵡 … z20 眾事/僧福/念淨命
  c7 傳云中國臨終…        <- z21 唱讀 ; z22 智論問答 ; z23 銅盌緣/慳衣緣(勸導科起)
  c8 其瞻病者…            <- z23 量機四觀察 ; z24 緣佛/心觀/隨緣
  c9 四分當問病者…        <- z25 問衣鉢 ; z26 面王 ; z27 難陀王緣 ; z28 勸捨慳/勸依法
  c10 應以經卷手執…       <- z29 華嚴偈 ; z30 新譯/善見/母論/打磬前
  c11 二明送終法…         <- z31 打磬末 + 第二送終敘意
  c12 初中當從像前…       <- z31 將屍出科起 ; z32 絹棺/坐處/布草 ; z33 不泣反非/吊慰次第 ; z34 五分/五百問/殯送
  c13 二明葬法…           <- z35 二率眾僧/貸亡物/葬法四葬 ; z36 火葬/香華/起塔 ; z37 增一四塔/露盤 ; z38 級重/立像起塔處 ; z39 增一輿母 ; z40 準下例決/善見白衣喪
"""
import io, json, os

B = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
D = os.path.join(B, "AI語譯", "_work", "align_fix2")
data = json.load(io.open(os.path.join(D, "001.json"), encoding="utf-8"))
items = data["items"]
cands = data["cand"]
cset = [c["c"] for c in cands]

cmap = [0, 1, 1, 2, 2, 3, 3, 3, 3, 4, 4, 4, 5, 6, 6, 6, 6, 6, 6, 6, 6,
        7, 7, 7, 8, 9, 9, 9, 9, 10, 10, 11, 12, 12, 12, 12, 13, 13, 13, 13, 13]

assert len(cmap) == len(items), (len(cmap), len(items))
res = [{"z": it["z"], "c": cmap[i]} for i, it in enumerate(items)]
assert [r["z"] for r in res] == list(range(len(items)))
assert all(r["c"] in cset for r in res)
assert all(res[i]["c"] <= res[i + 1]["c"] for i in range(len(res) - 1))

out = os.path.join(D, "out_001.json")
with io.open(out, "w", encoding="utf-8") as fh:
    fh.write(json.dumps({"map": res}, ensure_ascii=False, separators=(",", ":")))
print("written", out, "items", len(res))
print("dist", {c: sum(1 for r in res if r["c"] == c) for c in sorted(set(cmap))})
