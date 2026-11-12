# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2e_build3 as B
N = 1735
items = [
 (1, '讓你終身不得取證涅槃', '盡形壽不許入涅槃（滅度）', '涅槃=入滅非證果'),
 (2, '前往其餘諸洲', '前往其餘三洲', '漏譯三'),
 (4, '這也只是暫且依據一種普遍的相狀而言罷了', '這也只是姑且就一方面（一種情形）而言罷了', '一相=一方面'),
 (8, '隨約定的期限而一併滅除', '隨（受戒時）所要期的誓限而一同謝滅', '期=要誓'),
 (8, '便會將五戒、八戒、十戒、具足戒引申延長', '便會牽引五戒、八戒、十戒、具足戒使其延長至未來', '引令長'),
 (8, '歷經來生而本有的戒體仍在', '轉生之後，原先所受的戒若仍存在', '本戒=先前所受'),
 (9, '必定有人因宿命知見等昔日痕跡而得知自己有戒', '倘若因往世遺留的痕跡而確有得知自己有戒的人', '或有知者'),
 (12, '所以在律藏中規定', '所以律中說', '引律判果非條文'),
 (12, '受戒者得戒，能授僧眾結罪', '受者得戒、授者得罪', '得戒得罪'),
 (13, '豈不是志大浮誇的狂妄之徒嗎', '豈不是狂妄疏略、任意妄作嗎', '狂簡'),
 (6, '但自身內部則可相通', '但當分具戒可通攝五戒、十戒', '自通'),
]
verdicts = [
 dict(ref=1, kind='真錯', reason='涅槃'),
 dict(ref=2, kind='真錯', reason='三洲'),
 dict(ref=4, kind='真錯', reason='一相'),
 dict(ref=8, kind='真錯', reason='期=要誓'),
 dict(ref=8, kind='真錯', reason='本戒'),
 dict(ref=13, kind='真錯', reason='狂簡'),
 dict(ref=12, kind='真錯', reason='律中說'),
 dict(ref=9, kind='真錯', reason='或有知者'),
 dict(ref=8, kind='真錯', reason='引令長'),
 dict(ref=6, kind='真錯', reason='自通'),
 dict(ref=1, kind='誤報', reason='四部大眾'),
 dict(ref=1, kind='誤報', reason='八年補足'),
 dict(ref=5, kind='誤報', reason='約=就'),
 dict(ref=6, kind='誤報', reason='若若並列'),
 dict(ref=7, kind='誤報', reason='大小通局譯文可'),
 dict(ref=9, kind='誤報', reason='記主設問'),
 dict(ref=8, kind='誤報', reason='兩不失明指'),
 dict(ref=11, kind='誤報', reason='總示可解'),
]
B.make(N, items, verdicts)
