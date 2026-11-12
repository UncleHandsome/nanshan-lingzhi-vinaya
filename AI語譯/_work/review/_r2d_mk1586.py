# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import _r2d_build as B

I = []
def e(seq, old, new, why): I.append((seq, old, new, why))
e(2, "廣說則為九個品位", "廣說則為九類", "九品是法的分類，非品位")
e(3, "三種階位、九個品類", "三位、九類", "位品是分類，非階級")
e(6, "二十人實際上並非獨立體，四人才是真正的僧體", "二十人（連同五人、十人）並非真實的僧體，四人才是真實僧體", "實非／實是就真實僧體說，非獨立體")
e(6, "隨順時機而辨別", "隨其機緣便能成辦（法事）", "辨通辦，非辨別")
e(6, "人分為七個等級", "人分為七類", "七等是人數分類，非等級")
e(7, "「當身成用」即是根本的心念法", "「當身成用」即是但心念法", "本心念＝但心念，非另立根本")
e(10, "必須以成辦救濟為先決條件", "必以成辦濟事為首要", "濟＝濟事成辦，非救濟；為先＝首要")
e(10, "相互包攬檢驗", "相互檢括", "括＝檢括，非包攬")
e(11, "首先敘述羯磨教法的根本成否在於因緣", "先敘羯磨教法之本：成辦與否在於因緣", "斷句：敘羯磨教本／成否在緣")
e(11, "列舉法以包括因緣", "舉法以統括諸緣", "括＝統括，非包括")
e(15, "第二念（食處/夏數等）與第三念為二合事", "第二念（受緣）與第三念（夏數）為二合事", "二三念所屬錯置，且擅增食處")
e(15, "有的事務只對應一種，有的對應三種或兩種", "有的一法只對一事，或對二事、三事", "主客顛倒：一法所對之事或一二三")
V = [
  dict(seq=1, kind='誤報', reason='四相夾注'),
  dict(seq=2, kind='真錯', reason='九品位'),
  dict(seq=3, kind='真錯', reason='階位品類'),
  dict(seq=4, kind='誤報', reason='情事括注'),
  dict(seq=5, kind='已修', reason='#56無實質誤譯'),
  dict(seq=6, kind='真錯', reason='實非實是、辨、七等'),
  dict(seq=7, kind='真錯', reason='本心念'),
  dict(seq=8, kind='誤報', reason='隨文列相屬潤飾'),
  dict(seq=9, kind='誤報', reason='條界屬潤飾'),
  dict(seq=10, kind='真錯', reason='成濟、檢括'),
  dict(seq=11, kind='真錯', reason='教本斷句、括緣'),
  dict(seq=12, kind='誤報', reason='三條待核'),
  dict(seq=13, kind='已修', reason='#64無實質誤譯'),
  dict(seq=14, kind='誤報', reason='受緣括注'),
  dict(seq=15, kind='真錯', reason='二三念、一法對事'),
  dict(seq=16, kind='已修', reason='#67無實質誤譯'),
  dict(seq=17, kind='誤報', reason='別部之說屬潤飾'),
]
B.make(1586, I, V)
