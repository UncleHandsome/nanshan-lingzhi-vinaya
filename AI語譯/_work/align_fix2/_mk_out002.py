# -*- coding: utf-8 -*-
"""Build out_002.json for align_fix2 batch 002 (sec 27 諸雜要行, 記 47 段).

Mapping derived from 牒詞 + 義理順序 (記文連續，逐段回找所釋鈔段):
  c0  森然萬境…            <- z0 篇題（諸雜/要行）+ 初句示境廣
  z1 森然/次句/三違犯/四來報 ; z2 一一事/種種誡/諸門/別下 ; z3 統收/繁類/雜務/怯懦
  c1  十種分之…            <- z4 標列十門/一四五化制（次科多論起 c3）
  c3  薩婆多華瓔…          <- z5 華纓/五百問/佛臘（三中十誦起 c4）
  c4  十誦知僧事人…        <- z6 智論差次/從下起（四中～七中為 C5-C8 科）
  c8  僧祇果樹有功…        <- z7 一熟一剪/五分三段/僧物不分賣/結蘭
  c9  僧祇佛生日幡蓋…      <- z8 收舉補治/徐行（三中母論起 c10，第二門起 c11）
  c11 二眾中雜事…          <- z9 五法 ; z10 俯下仰上/四不雜語/五示默/善見辭謝
  c12 善見優波離…          <- z11 師子座/僧祇法座（三中入堂威儀起 c13）
  c13 打靜法…              <- z12 等得/打椎/制非法（第三門五問起 c14）
  c16 五分學書…            <- z13 學誦/世論/雜法/文頌 ; z14 草聖/智論外典 ; z15 善戒經/母論
  c17 五分剃髮…            <- z16 四中五分/無人難緣/母論簡剃處 ; z17 遺教論/兩月兩指 ; z18 頭鬚髮爪/增一五過
  c18 四分喜往白衣家…      <- z19 五中十過/五種非親厚
  c19 成論捨五慳…          <- z20 勝人（c18餘）+ 六中家慳（七中五寶、八中十事為 c20/c21 科）
  c21 十輪十事…            <- z21 睡眠/聽受供給（九中習方術起 c22）
  c22 四分賣卜誦呪…        <- z22 律下呪誓（十中恐怖起 c23）
  c25 四分嚼楊枝…          <- z23 大小二事/經行五益 ; z24 經行之基/三千作處（十三眾處燈起 c26）
  c26 僧祇然燈法…          <- z25 䩭/長明燈 ; z26 齊限/難陀女緣 ; z27 立誓/目連 ; z28 燈明不損/授記
  c27 五分乞兒乞狗…        <- z29 非人/母論人中別類（十五、十六、第四門為科）
  c30 四共行同法…          <- z30-z34 誦持/勝鬘/三學/要覽/三千/十誦
  c31 善見師猶在…          <- z35 恐怖（c30餘）/制廢忘/年別受/佛藏
  c32 多論顯德…            <- z36 無我人法/三中現通/沓婆
  c33 五出家要業…          <- z37 二是開緣（c32餘）/五中別修/正示僧本務
  c35 俗人造像…            <- z38 三佛/聞思修/僧寶/宮殿（三中結歎、引證為 c36/c37 科）
  c38 智論出家多修智慧…    <- z39 樂因緣/僧祇/受戒說相（六中四分被劫起 c39）
  c39 六遇賊法…            <- z40 得折草/白衣外道服（次科母論、十誦、僧祇為 c40）
  c41 七大小便法…          <- z41 洗穢/制餘務/六法/留殘水
  c42 五分小便器…          <- z42 七土洗/五分三事/三千（第八中起 c43）
  c43 八慈濟畜生法…        <- z43 壞網及獄/猪下餘語（九中起 c44）
  c44 九避惡畜生法…        <- z44 櫺子/拾蝨（十中起 c45）
  c45 十雜明治病法…        <- z45 無者/五百問/法僧傳
  c46 四分學呪治病…        <- z46 唾腫（c45餘）/教學呪/患吐患熱/腐爛藥
"""
import io, json, os

B = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
D = os.path.join(B, "AI語譯", "_work", "align_fix2")
data = json.load(io.open(os.path.join(D, "002.json"), encoding="utf-8"))
items = data["items"]
cands = data["cand"]
cset = [c["c"] for c in cands]
print("items", len(items), "cands", len(cands))

cmap = [0, 0, 0, 0, 1, 3, 4, 8, 9, 11, 11, 12, 13, 16, 16, 16, 17, 17, 17,
        18, 19, 21, 22, 25, 25, 26, 26, 26, 26, 27, 30, 30, 30, 30, 30,
        31, 32, 33, 35, 38, 39, 41, 42, 43, 44, 45, 46]

assert len(cmap) == len(items), (len(cmap), len(items))
res = [{"z": it["z"], "c": cmap[i]} for i, it in enumerate(items)]
assert [r["z"] for r in res] == list(range(len(items)))
assert all(r["c"] in cset for r in res), [r for r in res if r["c"] not in cset]
assert all(res[i]["c"] <= res[i + 1]["c"] for i in range(len(res) - 1))

out = os.path.join(D, "out_002.json")
with io.open(out, "w", encoding="utf-8") as fh:
    fh.write(json.dumps({"map": res}, ensure_ascii=False, separators=(",", ":")))
print("written", out, "items", len(res))
print("dist", {c: sum(1 for r in res if r["c"] == c) for c in sorted(set(cmap))})
print("unused", [c for c in cset if c not in set(cmap)])
