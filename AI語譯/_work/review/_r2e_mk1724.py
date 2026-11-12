# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2e_build3 as B
N = 1724
items = [
 (1, '「彼此」，就是俗世與道門', '「彼此」，就是指在家人與出家人', '道門非道教'),
 (1, '戒體卻尚未納受僧法', '其身分卻尚未納受出家戒法', '體=身分本質非戒體'),
 (1, '領納戒法是依據實質戒體，而不論外在形貌的緣故', '領受戒法是就其實際身分來判定，不論外形的緣故', '受法約體'),
 (1, '大多在俗時就已經受了五戒', '多有人在俗時就已受了五戒', '多有非大多'),
 (1, '所以省略了受五戒的程序', '所以（律文）就略而不說', '故略之=律文省略'),
 (1, '此文出自〈大持小持犍度〉', '此文出自〈大小持戒犍度〉', '犍度名'),
 (1, '是指律典前後除此〈大小持犍度〉之外再無其他文據', '是指遍查律典前後文，關於此事除此段大小持文外別無他文', '範圍擴大'),
 (1, '如同比丘羯磨計算成辦人數（足數）時', '如同比丘「足數」（湊足羯磨僧數）的規定中', '足數術語'),
 (1, '其餘詳如下文漸受、頓受與捨戒各篇', '其餘詳如下文「漸頓受捨」一節', '漸頓受捨一節非各篇'),
 (3, '陷害了自己與他人', '使自他都陷於缺失', '陷=陷失非陷害'),
 (6, '在第二項作法中區分為文辭本體與結告兩項', '在第二科受法中，將文分為「體」與「結」兩部分', '文體斷句'),
 (10, '因此疏文沒有詳細解說', '所以（記文）就不詳細開示了', '記主自述非疏文'),
 (10, '至於其餘受戒者既然已經明曉', '至於其餘（八戒等）既已明白', '自餘非指人'),
 (10, '十戒是真正步入解脫道的伊始', '十戒是入出家之道的伊始', '入道非解脫道'),
 (12, '其果位堪能受納眾生信施供養', '其身分地位堪能接受眾生供養', '沙彌非果位'),
]
verdicts = [
 dict(ref=1, kind='真錯', reason='道門'),
 dict(ref=1, kind='真錯', reason='受法約體'),
 dict(ref=1, kind='真錯', reason='體未納法'),
 dict(ref=1, kind='真錯', reason='多有'),
 dict(ref=1, kind='真錯', reason='故略之'),
 dict(ref=1, kind='真錯', reason='大小持犍度'),
 dict(ref=1, kind='真錯', reason='律上下範圍'),
 dict(ref=1, kind='真錯', reason='足數'),
 dict(ref=1, kind='真錯', reason='漸頓受捨'),
 dict(ref=1, kind='誤報', reason='餘廣如別潤飾'),
 dict(ref=3, kind='真錯', reason='自他陷也'),
 dict(ref=3, kind='誤報', reason='隨機/例須舉/本原'),
 dict(ref=4, kind='存疑', reason='十三輕遮'),
 dict(ref=4, kind='誤報', reason='如善見指注文'),
 dict(ref=4, kind='誤報', reason='境量'),
 dict(ref=5, kind='誤報', reason='正受法體結句'),
 dict(ref=6, kind='真錯', reason='文體斷句'),
 dict(ref=7, kind='誤報', reason='別指所重'),
 dict(ref=7, kind='誤報', reason='歸三境'),
 dict(ref=7, kind='誤報', reason='調達別部'),
 dict(ref=8, kind='誤報', reason='示須牒意'),
 dict(ref=10, kind='真錯', reason='不委示'),
 dict(ref=10, kind='真錯', reason='自餘已曉'),
 dict(ref=10, kind='真錯', reason='入道'),
 dict(ref=11, kind='誤報', reason='五德十數術語'),
 dict(ref=12, kind='真錯', reason='果位'),
 dict(ref=12, kind='誤報', reason='大福田增字'),
 dict(ref=2, kind='誤報', reason='法同法體例'),
]
B.make(N, items, verdicts)
