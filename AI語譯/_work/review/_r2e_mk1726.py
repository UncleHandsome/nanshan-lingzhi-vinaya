# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2e_build3 as B
N = 1726
items = [
 (1, '因此下文引文為證', '「故」字以下，是引經證成', '故下=科判故字以下'),
 (6, '這五種美德從初發心到究竟解脫貫通於出家五眾', '這五種美德從受戒之初直到盡形壽，貫通於出家五眾', '始終=初受至盡形壽'),
 (8, '正如律文中所列', '如疏文所列', '文=疏文'),
 (9, '西印度天竺的外道總括有六大宗師', '西方天竺（印度）的外道總括有六大宗師', '西竺=西方天竺非西印度'),
 (11, '如同比丘戒本中「食家有寶」中的「食家」即指觸食之處', '如同比丘戒本中「食家有寶」，這「食家」正是以男女相觸為食之家', '食家=男女相觸為食'),
 (12, '本非正信之師', '本來不是正法中人，而是外道邪徒', '本非正師'),
 (4, '奉行無上至極的大乘圓融教法，普濟兼度他人', '奉行至極之教（大乘），兼帶濟度他人', '圓融/普濟增譯'),
 (7, '所以可以作為世間師範', '所以可以作為人天師範', '漏譯人天'),
 (10, '或者服食丹藥以保全生命', '或者服食藥物以保全生命', '丹為增字'),
 (11, '便能任持眼等諸根與四大造色令其不毀滅敗壞', '便能任持諸根與四大及所造色令其不毀滅敗壞', '大造=四大及所造'),
 (11, '「思食」舉卵生為例只是暫取一種特相', '「思食」舉卵生為例只是偏舉一端', '一相=偏舉一端'),
]
verdicts = [
 dict(ref=1, kind='真錯', reason='故下引證'),
 dict(ref=6, kind='真錯', reason='始終'),
 dict(ref=8, kind='真錯', reason='如文'),
 dict(ref=9, kind='真錯', reason='西竺'),
 dict(ref=11, kind='真錯', reason='食家'),
 dict(ref=12, kind='真錯', reason='本非正師'),
 dict(ref=4, kind='真錯', reason='極教兼濟'),
 dict(ref=7, kind='真錯', reason='人天師範'),
 dict(ref=10, kind='真錯', reason='餌藥'),
 dict(ref=11, kind='真錯', reason='諸根大造'),
 dict(ref=11, kind='真錯', reason='且取一相'),
 dict(ref=2, kind='誤報', reason='委命譯文可'),
 dict(ref=11, kind='誤報', reason='反切未譯'),
 dict(ref=12, kind='誤報', reason='賊住未註'),
 dict(ref=11, kind='誤報', reason='初標示/通該潤飾'),
 dict(ref=7, kind='誤報', reason='示須說意'),
 dict(ref=10, kind='誤報', reason='濟神'),
 dict(ref=9, kind='誤報', reason='六師人名校註'),
 dict(ref=13, kind='誤報', reason='九月便生潤飾'),
 dict(ref=5, kind='誤報', reason='兼濟譯法'),
]
B.make(N, items, verdicts)
