# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import _r2d_build as B

I = []
def e(seq, old, new, why): I.append((seq, old, new, why))
e(4, "是為了簡別其他文句的緣故", "用以簡別律中其餘（非羯磨）之文", "餘文＝律中其餘部分")
e(4, "疏通決斷疑難窒礙，必定能使未明白的人", "疏通開決疑惑壅塞，使不明白的人（原文作「必」，疑「使」之訛）", "決＝開決；必疑使訛")
e(4, "雖然加上了註釋", "（道宣）雖已加以註釋", "主語懸空")
e(4, "使大小川澤得以疏導流通", "使河川湖澤得以疏通", "川澤非大小")
e(4, "序的含義如同通常所說，臨近正文自會列出闡述。", "「序」的意思如常途所說，隨文解釋時自會提出。", "臨文非臨近正文")
e(5, "大唐沙門釋道宣於終南山豐德寺撰", "唐朝沙門釋道宣在終南山豐德寺撰述", "撰號未譯")
e(6, "指明作者的名稱稱號", "指明作者的名號", "名稱稱號贅")
e(6, "依據《高僧傳》，原名豐谷寺", "依據《僧傳》（原文僅作「僧傳」，或指《續高僧傳》），原名豐谷寺", "坐實高僧傳")
e(6, "「撰」解釋為述作，表現作者的謙遜。", "「撰」字訓解為「述」（只是傳述前人舊說，不敢自居創作），表示謙遜。", "述作抹掉謙意")
e(6, "依據下文評點批註之文", "依據下文的批記之文", "評點語感不妥")
e(7, "審察聖人示現於世間", "試看佛陀應機出現於世（令眾生見而得益）", "觀夫係發語詞")
e(7, "作為言教宗旨", "作為言教", "宗旨係增字")
V = [
 dict(seq=1, kind='誤報', reason='目錄照抄屬體例'),
 dict(seq=2, kind='已修', reason='#8正確'),
 dict(seq=3, kind='誤報', reason='標題保留可'),
 dict(seq=4, kind='真錯', reason='疏決非決斷'),
 dict(seq=4, kind='真錯', reason='臨文自舉'),
 dict(seq=4, kind='真錯', reason='必不曉增字'),
 dict(seq=4, kind='真錯', reason='簡餘文'),
 dict(seq=4, kind='真錯', reason='雖加注釋主語'),
 dict(seq=4, kind='真錯', reason='川澤'),
 dict(seq=4, kind='誤報', reason='故也、上皆所序屬體例潤飾'),
 dict(seq=5, kind='真錯', reason='撰號未譯'),
 dict(seq=6, kind='真錯', reason='撰即訓述'),
 dict(seq=6, kind='真錯', reason='僧傳坐實'),
 dict(seq=6, kind='真錯', reason='準下批文'),
 dict(seq=6, kind='真錯', reason='名稱稱號'),
 dict(seq=6, kind='誤報', reason='記文標示等屬體例'),
 dict(seq=7, kind='真錯', reason='觀夫發語詞'),
 dict(seq=7, kind='真錯', reason='以為言焉增宗旨'),
 dict(seq=7, kind='誤報', reason='界繫四倒補注即可'),
]
B.make(1560, I, V)
