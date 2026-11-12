# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import _r2d_build as B

I = []
def e(seq, old, new, why): I.append((seq, old, new, why))
e(1, "考量這一個法門", "考量這一科", "一門＝一科，非「法門」")
e(1, "然而學識博洽乃是總攝教務的資糧", "然而學識博洽乃是成辦事務的資助", "攝務＝成辦事務，非總攝教務")
e(2, "用竹管窺測青天，用鐵錐測量大地", "用竹管窺天，用錐子指地", "刪增譯「青」「鐵」，回歸《莊子》原文")
e(6, "自「故」以下引用解釋名稱", "自「故」以下引用釋文來解釋名稱", "引解釋名＝引釋文釋名")
e(7, "所立下約定時間與事相各自具有具體相貌的緣故", "所立的禁制，無論就時間或就事相而言，都各有其相貌的緣故", "斷句：所立／約時約事各有相貌")
e(7, "論疏解釋說：例如僧團立下規約", "該論解釋說：例如僧團立下規約", "解云是論自釋，非論疏")
e(9, "論疏解釋說：唱告所要立辦的事務", "該論解釋說：唱告所要立辦的事務", "解云是論自釋，非論疏")
e(11, "是指單純唱告一分宣告文、一分羯磨文", "是指只唱白的一部分、羯磨的一部分", "白一分、羯磨一分＝各一分，皆不具足")
e(12, "接著引用論疏解釋", "接著引用該論的解釋", "解云是論自釋，非論疏")
V = [
  dict(seq=1, kind='真錯', reason='攝務、一門'),
  dict(seq=2, kind='真錯', reason='莊子引文增譯'),
  dict(seq=3, kind='誤報', reason='三品點名屬加註'),
  dict(seq=4, kind='誤報', reason='三律點名屬加註'),
  dict(seq=5, kind='已修', reason='#100無實質誤譯'),
  dict(seq=6, kind='真錯', reason='引解釋名句法'),
  dict(seq=7, kind='真錯', reason='時量斷句、論疏'),
  dict(seq=8, kind='誤報', reason='約字屬潤飾'),
  dict(seq=9, kind='真錯', reason='論疏'),
  dict(seq=10, kind='已修', reason='#105無實質誤譯'),
  dict(seq=11, kind='真錯', reason='白一分羯磨一分'),
  dict(seq=12, kind='真錯', reason='論疏'),
  dict(seq=13, kind='已修', reason='#108無實質誤譯'),
  dict(seq=14, kind='已修', reason='#109無實質誤譯'),
  dict(seq=15, kind='誤報', reason='僧人數、缺文屬加註'),
]
B.make(1574, I, V)
