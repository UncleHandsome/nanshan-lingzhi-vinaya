# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2e_build3 as B
N = 1736
items = [
 (7, '上品心受具足戒，原先在俗的五戒仍屬下品，沙彌的十戒屬中品，其餘具足戒戒條才屬上品', '上品心受具足戒，（十戒中的）前五戒仍屬下品，沙彌（所增的後五戒）屬中品，其餘（二百四十條）才是上品', '沙彌是中指後五戒'),
 (8, '沙彌的後五戒與具足戒共同受約束', '沙彌十戒的後五戒，十戒與具足戒也都同樣約束', '十具齊約'),
 (8, '戒體不再重疊倍增', '戒體不會重發增益（前受者不隨後受而升級）', '體無重增'),
 (8, '且如五戒在三種身分中都同樣禁止', '譬如五戒這五條，俗人、沙彌、比丘三種人都同樣禁持', '五戒三種俱禁'),
 (6, '恐有人懷疑合併受戒會獲得三種戒體', '恐怕有人疑惑：同時併受是否會分別得到三種戒體，故設此問', '疑情語氣'),
 (6, '是指戒體通貫三種戒', '是指一個戒體通於三種身分（俗人、沙彌、比丘）', '體通三'),
 (5, '統統具備無作戒體，並沒有另外單獨的五戒與十戒', '（一時頓受者）三戒都具足無作戒體，但並非另有別體的五戒、十戒', '俱具無作主語'),
 (12, '受戒局限而捨戒相通', '受戒只限於漸次，捨戒則通於漸捨與頓捨', '受局捨通'),
 (13, '經文明列大愛道先受五戒', '律文明列大愛道先受五戒', '文=律文'),
 (14, '則容許兼有五戒與十戒兩種', '則可能兼有五戒與十戒兩種', '容=或許'),
]
verdicts = [
 dict(ref=7, kind='真錯', reason='沙彌是中'),
 dict(ref=8, kind='真錯', reason='十具齊約'),
 dict(ref=8, kind='真錯', reason='體無重增'),
 dict(ref=6, kind='真錯', reason='疑情語氣'),
 dict(ref=6, kind='真錯', reason='體通三'),
 dict(ref=5, kind='真錯', reason='俱具無作'),
 dict(ref=12, kind='真錯', reason='受局捨通'),
 dict(ref=13, kind='真錯', reason='文列五戒'),
 dict(ref=14, kind='真錯', reason='容兼二戒'),
 dict(ref=8, kind='真錯', reason='五戒三種'),
 dict(ref=7, kind='誤報', reason='形俱無作加註'),
 dict(ref=1, kind='誤報', reason='志向喜好潤飾'),
 dict(ref=2, kind='誤報', reason='次科'),
 dict(ref=3, kind='誤報', reason='次第名位'),
 dict(ref=4, kind='誤報', reason='葉譬本質'),
 dict(ref=9, kind='誤報', reason='亦望'),
 dict(ref=10, kind='誤報', reason='通括之答'),
 dict(ref=12, kind='誤報', reason='更無所留加註'),
 dict(ref=13, kind='誤報', reason='直本白衣'),
 dict(ref=11, kind='誤報', reason='受局捨通結示'),
]
B.make(N, items, verdicts)
