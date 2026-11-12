# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2e_build3 as B
N = 1725
items = [
 (3, '具足戒受體浩瀚卻只宣示四重戒相', '受具足戒者只宣示四重戒相', '受體浩瀚為增譯'),
 (3, '為新受戒比丘宣說僧殘等下篇戒相', '為新受戒比丘宣說僧殘（第二篇）', '等字誤擴'),
 (4, '這依然是不可毀犯的戒律分位', '這仍屬「戒分」（初二篇為戒分）', '戒分術語'),
 (4, '因為殘害僧團體制同等嚴重的緣故', '因為它與初篇同樣敗壞僧眾的緣故', '壞眾非體制'),
 (4, '所以受戒時暫且不說', '所以（僧殘以下）也就不說', '補主語'),
 (7, '疏文梵語與華語並舉', '戒文梵語與華語並舉', '戒文非疏文'),
 (7, '「金」、「色」都是漢土華夏之語', '（四分的）「金」就是（僧祇的）「色」，二者都是唐言', '即金為色漏譯'),
 (15, '「靡」就是妖豔美麗', '「靡」就是美麗', '妖豔增譯'),
 (16, '瓦鉢挑在肩頭', '瓦缽穿繩掛在肩上', '貫肩'),
 (5, '只是增加了最後一條「捉持金寶」', '只是增加了最後一條「不捉持金銀寶物」', '戒條遮止'),
 (1, '正如律文中〈大持小持犍度〉所說', '正如律文中〈大小持戒犍度〉所說', '犍度名'),
 (1, '是完整具受身三口四等七支戒體', '是完整具受身三口四七支戒體', '刪等字'),
 (6, '八關齋戒若將歌舞觀聽與香油塗身分開為二便成九條', '八關齋戒若將「香華鬘」與「香塗身」分開為二便成九條', '開九所指'),
 (10, '如同疏文引用經典所說', '如同注文所引用經典所說', '如文=注文'),
]
verdicts = [
 dict(ref=3, kind='真錯', reason='受體浩瀚'),
 dict(ref=3, kind='真錯', reason='下篇等字'),
 dict(ref=4, kind='真錯', reason='戒分'),
 dict(ref=4, kind='真錯', reason='壞眾'),
 dict(ref=4, kind='真錯', reason='故亦不說'),
 dict(ref=7, kind='真錯', reason='梵唐兩舉'),
 dict(ref=7, kind='真錯', reason='即金為色'),
 dict(ref=15, kind='真錯', reason='妖豔'),
 dict(ref=16, kind='真錯', reason='貫肩'),
 dict(ref=5, kind='真錯', reason='捉持金寶'),
 dict(ref=1, kind='真錯', reason='大小持犍度'),
 dict(ref=1, kind='誤報', reason='等字七支'),
 dict(ref=6, kind='真錯', reason='開九所指'),
 dict(ref=10, kind='真錯', reason='如文=注文'),
 dict(ref=1, kind='誤報', reason='約緣明十潤飾'),
 dict(ref=2, kind='誤報', reason='戒相通數'),
 dict(ref=2, kind='誤報', reason='持奉行同'),
 dict(ref=8, kind='誤報', reason='縱古/如下示'),
 dict(ref=13, kind='誤報', reason='正字義'),
 dict(ref=14, kind='誤報', reason='易性/之見'),
 dict(ref=12, kind='誤報', reason='情厭諸有'),
 dict(ref=11, kind='誤報', reason='如文=注文（五德）'),
 dict(ref=9, kind='誤報', reason='敕令受持'),
 dict(ref=4, kind='誤報', reason='太僧校註'),
 dict(ref=16, kind='存疑', reason='居知誰可愛憎'),
]
B.make(N, items, verdicts)
