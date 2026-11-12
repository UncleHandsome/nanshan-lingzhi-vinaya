# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import _r2d_build as B

I = []
def e(seq, old, new, why): I.append((seq, old, new, why))
e(1, "並非由僧團全體行懺", "並非用僧法（眾法羯磨）行懺", "僧懺＝僧法懺，非「全體」")
e(5, "到了作羯磨法時，界內的僧眾也通通收攝在內", "等到實際作法時，界內之人也同樣收攝在內", "悔蘭是對首法，非羯磨；界亦通收指界內有人不得別")
e(6, "《四分律》指的就是〈滅諍犍度〉，所以稱為「下文」", "所引《四分》之文即出於〈滅諍犍度〉（在後文），所以說是「下文」", "引文出處誤作整部律；滅諍犍度是出處")
e(6, "就必須推崇說戒與自恣", "就應推許說戒、自恣居於上位", "推＝推與居上，非推崇")
e(6, "起初是比對捨墮以顯明通達與局限", "起初是比對捨墮以顯明「通」（可通一人）與「局」（限於二、三人）的差別", "通非通達，通局就人數言")
e(6, "所以列為上品", "所以在對首三位中居於上位", "悔蘭是中上，非九品之上品")
e(9, "牽涉情節繁多", "所對之人眾多", "情指有情／對境之人，非情節")
V = [
  dict(seq=1, kind='真錯', reason='僧懺非全體'),
  dict(seq=2, kind='誤報', reason='會通等屬潤飾'),
  dict(seq=3, kind='已修', reason='#77無實質誤譯'),
  dict(seq=4, kind='已修', reason='#78無實質誤譯'),
  dict(seq=5, kind='真錯', reason='及時加法非羯磨'),
  dict(seq=6, kind='真錯', reason='四分出處、推說恣、通局、上品'),
  dict(seq=7, kind='誤報', reason='此豈為中語氣屬潤飾'),
  dict(seq=8, kind='誤報', reason='自可違制屬潤飾'),
  dict(seq=9, kind='真錯', reason='情多＝所對人眾'),
]
B.make(1572, I, V)
