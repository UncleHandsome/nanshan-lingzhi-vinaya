# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2e_build3 as B
N = 1759
items = [
 (8, '已經把各難收攝殆盡了', '已經把各難全部收盡、無有遺漏', '殆盡用詞'),
 (9, '在收攝殆盡的第一科中', '在「攝盡」的第一科中', '殆盡用詞'),
 (3, '偷住賊住的人', '賊住之人（未受具戒卻冒稱比丘、混住僧中者）', '偷住=賊住'),
 (17, '後面這幾種人本來就沒有求受戒之心', '這些（八難中的）眾生本來就沒有求受戒之心', '此指八難眾'),
 (13, '律中記載九歲的和尚度人', '律中記載戒臘九夏的和尚度人', '九歲=九夏'),
 (8, '具有心識前來乞戒', '有求戒之心而來乞戒', '有心=求戒心'),
 (12, '正面的制度規定難以違背', '這是律的明文正制，不可違背', '正制難違'),
 (4, '這類人實在為數眾多，此處暫且列舉十三種', '實則這類情形還有很多，（律中）只是暫列十三難', '乃有眾也'),
 (9, '也就是三途八難之難', '也就是（障聞法的）八難', '八難'),
 (6, '全都是戒體之障', '都是得戒的障礙', '戒障'),
 (10, '如同前面所說體性永遠固定不變', '如前所說，是永遠決定不得戒的', '永定'),
 (15, '所以不能相互收攝', '所以（八難）不為十三難所收攝', '不攝'),
 (12, '由於外緣疏遠而受戒的正因端正，所以得戒並無不同', '和尚年不滿只是外緣（關係疏遠），受戒者本人的正因具足，所以弟子得戒與和尚滿十夏時並無不同', '緣疎因正'),
 (2, '永久啞巴、永久聾子', '永遠瘖啞者、永遠耳聾者', '文體'),
]
verdicts = [
 dict(ref=8, kind='真錯', reason='殆盡'),
 dict(ref=9, kind='真錯', reason='殆盡'),
 dict(ref=3, kind='真錯', reason='偷住'),
 dict(ref=17, kind='真錯', reason='此指八難'),
 dict(ref=13, kind='真錯', reason='九歲和尚'),
 dict(ref=8, kind='真錯', reason='有心'),
 dict(ref=12, kind='真錯', reason='正制難違'),
 dict(ref=4, kind='真錯', reason='乃有眾也'),
 dict(ref=9, kind='真錯', reason='八難'),
 dict(ref=6, kind='真錯', reason='戒障'),
 dict(ref=10, kind='真錯', reason='永定'),
 dict(ref=15, kind='真錯', reason='不攝'),
 dict(ref=12, kind='真錯', reason='緣疎因正'),
 dict(ref=2, kind='真錯', reason='瘖啞'),
 dict(ref=4, kind='存疑', reason='六種計數'),
 dict(ref=17, kind='存疑', reason='又云歸屬'),
 dict(ref=1, kind='誤報', reason='方便即止加註'),
 dict(ref=3, kind='誤報', reason='十種是難加註'),
 dict(ref=12, kind='誤報', reason='類彼式叉'),
 dict(ref=9, kind='誤報', reason='八難含三途'),
]
B.make(N, items, verdicts)
