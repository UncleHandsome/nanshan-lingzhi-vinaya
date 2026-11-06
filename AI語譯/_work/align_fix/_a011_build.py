# -*- coding: utf-8 -*-
"""Build out_011.json for align_fix batch 011 (sec 14 隨戒釋相, 記 z750-899).

記段 -> 鈔段 (c index in 011.json cand) derived from the 牒詞 / 義理順序 of the
資持記 against the 行事鈔 section, using the full paragraphs of both texts
(_a011_Z.txt / _a011_C.txt) plus the 戒 numbering marks (「二十一」「第二」…):

  c130 販賣戒二十            z750-z758  三中/四中…十中, 僧祇八物相貿
  c131 畜長鉢過限戒二十一     z759-z760  二十一緣, 犯緣第三/第四, 《善見》, 指略
  c132 乞鉢戒二十二           z761       五綴, 不漏吉, 不犯八緣
  c133 自乞縷使非親織戒二十三 z762-z764  二十三緣/制意/犯緣, 四句, 開自織
  c134 勸織師增衣縷戒二十四   z765       許直, 四分, 多論, 疏問
  c135 奪衣戒二十五           z766-z767  二十五緣, 三中四句, 不犯有八
  c136 畜七日藥過限戒二十六   z768-z771  二十六緣, 指廣, 藥體, 五無緣, 不犯
  c137 過前求雨衣戒二十七     z772-z777  犯相, 過用, 衣體, 六制, 捨法
  c138 過前受急施衣戒二十八   z778-z781  急施, 過前/過後, 時非時
  c139 有難蘭若離衣戒二十九   z782-z788  名中, 疑怖, 五分/善見, 斥古, 問答
  c140 說迴僧物入已戒三十     z789-z791  戒名, 三種, 五相, 吉/重
  c141 九十中小妄語戒一       z792-z813  初戒, 敘意, 犯緣, 四句, 三時, 默妄
  c142 罵戒二                 z814-z827  第二, 戒名, 智論, 六諍本, 三行罵法
  c143 兩舌戒三               z828-z833  第三, 名中, 僧祇七事, 多論, 不犯
  c144 共女人宿戒四           z834-z841  第四, 女相/室相, 多論善見, 不犯九室
  c145 共未受具人宿戒五       z842-z845  第五, 宿限, 十誦/母論/僧祇, 多論四句
  c146 與未具人同誦戒六       z846-z849  第六, 四意, 句義/句味/字義, 不犯
  c147 向非具人說麁罪戒七     z850-z853  第七, 破法身, 緣中, 三中, 不犯
  c148 實得道向未具說戒八     z854-z855  第八, 多論二義, 疏文緣相, 問答
  c149 與女人說法過限戒九     z856-z859  第九, 過限, 釋第三/第六, 不犯中四
  c150 掘地戒十               z860-z870  第十, 制意, 犯緣, 地相, 十誦/多論/僧祇
  c151 壞生種戒十一           z871-z880  十一, 戒名, 五種, 五果, 行護十一節
  c152 身口綺戒十二           z881-z884  十二, 餘語/觸惱, 成論, 不犯
  c153 嫌罵僧知事戒十三       z885-z888  十三, 名中, 五分/四分, 百頭魚緣
  c154 露敷僧物戒十四         z889-z894  十四, 多論三義, 五分/僧祇, 四分四種
  c155 覆處敷僧物戒十五       z895       分二戒, 出界/三宿, 釋中
  c156 強敷戒十六             z896-z897  十六, 中間/臥具, 十誦, 不犯
  c157 牽他出僧房戒十七       z898-z899  十七, 犯緣, 牽出犯重/持物犯輕

Boundary rule: a 記段 that closes the previous 戒 and only heads the next
(緣起/科文 dangling) stays with the previous c; a 記段 whose body actually
explains the next 鈔段 takes that c.
"""
import json, io, os

AD = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_fix"
d = json.load(io.open(os.path.join(AD, "011.json"), encoding="utf-8"))
items, cand = d["items"], d["cand"]
n, m = len(items), len(cand)
z0 = items[0]["z"]

BLOCKS = [
    (130, 9),   # z750-z758
    (131, 2),   # z759-z760
    (132, 1),   # z761
    (133, 3),   # z762-z764
    (134, 1),   # z765
    (135, 2),   # z766-z767
    (136, 4),   # z768-z771
    (137, 6),   # z772-z777
    (138, 4),   # z778-z781
    (139, 7),   # z782-z788
    (140, 3),   # z789-z791
    (141, 22),  # z792-z813
    (142, 14),  # z814-z827
    (143, 6),   # z828-z833
    (144, 8),   # z834-z841
    (145, 4),   # z842-z845
    (146, 4),   # z846-z849
    (147, 4),   # z850-z853
    (148, 2),   # z854-z855
    (149, 4),   # z856-z859
    (150, 11),  # z860-z870
    (151, 10),  # z871-z880
    (152, 4),   # z881-z884
    (153, 4),   # z885-z888
    (154, 6),   # z889-z894
    (155, 1),   # z895
    (156, 2),   # z896-z897
    (157, 2),   # z898-z899
]
MAP = []
for c, k in BLOCKS:
    MAP += [c] * k

assert len(MAP) == n == 150, (len(MAP), n)
assert all(0 <= c < m for c in MAP)
assert all(MAP[i] <= MAP[i + 1] for i in range(n - 1))

out = {"map": [{"z": it["z"], "c": MAP[i]} for i, it in enumerate(items)]}
io.open(os.path.join(AD, "out_011.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, separators=(",", ":")))

# ---- validation ----
back = json.load(io.open(os.path.join(AD, "out_011.json"), encoding="utf-8"))
mp = back["map"]
print("entries", len(mp), "items", len(items), "ok", len(mp) == len(items))
print("z ok", [x["z"] for x in mp] == [it["z"] for it in items])
cs = [x["c"] for x in mp]
print("monotone", cs == sorted(cs), "| in cand", all(0 <= c < m for c in cs),
      "| distinct", len(set(cs)), "| min/max", min(cs), max(cs))
# every block's 記 must open with the expected 牒/戒號
checks = {
    130: "彼既決捨", 131: "言據有者", 132: "五綴共一尺也", 133: "自有買者",
    134: "許直者", 135: "二十五", 136: "或可無緣面奪", 137: "犯相既異",
    138: "忽有急緣", 139: "二十九", 140: "疏云：許僧物者", 141: "四分律行事鈔資持記中三上",
    142: "第二", 143: "四云教授", 144: "律文更列壞僧", 145: "等一指餘義者",
    146: "具斯四益", 147: "二同業者", 148: "名云實得道者", 149: "過限，謂五六語",
    150: "第一此戒則傷害", 151: "指緣同前", 152: "除經行土者", 153: "如常所開",
    154: "若下，相因而制", 155: "疏云：所以分二戒者", 156: "不下，結犯",
    157: "十七。〔佛在舍衛",
}
bad = []
for i, it in enumerate(items):
    if i == 0 or MAP[i] != MAP[i - 1]:
        k = checks.get(MAP[i])
        if k and k not in it["text"] and k not in items[i]["text"]:
            bad.append((it["z"], MAP[i], k))
print("block-opening checks failed:", bad)
