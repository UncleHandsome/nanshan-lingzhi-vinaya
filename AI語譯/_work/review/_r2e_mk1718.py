# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2e_build3 as B
N = 1718
items = [
 (10, '首先指示本著作（今本業疏）的做法；自「如下」以下，其次斥責他人的著作', '首先顯示今家羯磨本的作法；自「如下」以下，其次破斥他家的羯磨文', '今本=今家羯磨本非業疏'),
 (1, '依照戒臘安居坐夏', '依夏臘（戒臘）次第而坐', '依夏坐=依夏臘坐次'),
 (2, '「自無染」，是指自己無有貪染過失', '「自無染」，是指自己無有貪染過失，即是自利', '漏譯自利'),
 (5, '其標題與義理的解釋如同前文所述', '其標題與義釋（標下子注）如同前文所述', '義釋=標下子注'),
 (2, '不懂得權巧方便的深意', '不懂得那是聖位菩薩的權巧示現之行', '不知權行'),
 (7, '說明請求度化也就是蓄徒收眾之法', '說明乞求（僧眾聽許）度人，也就是畜眾之法', '乞度=乞僧聽許度人'),
 (12, '是說明寄託為制戒因緣的過失', '是說明藉以制戒的因緣過失', '託緣=依託因緣'),
 (4, '是說眾生的心體本來就是光明沉靜的', '是說眾生的心體本來就是明淨寂靜的', '明靜=明淨寂靜'),
 (1, '由於具備殊勝智慧與善巧方便，即使行持殺生等事，若能帶來大利益，自身便無染污之過失', '由於具備殊勝智慧與善巧方便，而具行殺生等事，因為有利益的緣故，自身便無染污之過失', '具行殺生非讓步仮設'),
 (2, '外在妄塵本來虛妄', '外在六塵本來空無', '本無=本來無有'),
]
verdicts = [
 dict(ref=10, kind='真錯', reason='今本'),
 dict(ref=1, kind='真錯', reason='依夏坐'),
 dict(ref=2, kind='真錯', reason='自利漏譯'),
 dict(ref=5, kind='真錯', reason='義釋'),
 dict(ref=2, kind='真錯', reason='不知權行'),
 dict(ref=7, kind='真錯', reason='乞度'),
 dict(ref=12, kind='真錯', reason='託緣'),
 dict(ref=4, kind='真錯', reason='明靜'),
 dict(ref=1, kind='真錯', reason='具行殺生'),
 dict(ref=2, kind='真錯', reason='外塵本無'),
 dict(ref=2, kind='誤報', reason='急護同潤飾'),
 dict(ref=2, kind='誤報', reason='互有所缺潤飾'),
 dict(ref=7, kind='誤報', reason='就文依位分加註'),
 dict(ref=7, kind='誤報', reason='簡師攝護'),
 dict(ref=8, kind='誤報', reason='分文可解'),
 dict(ref=4, kind='誤報', reason='幽遠潤飾'),
 dict(ref=9, kind='誤報', reason='男女僧尼贅字'),
 dict(ref=7, kind='誤報', reason='蓄徒蓄養體例'),
 dict(ref=1, kind='誤報', reason='大利益增字'),
 dict(ref=2, kind='誤報', reason='凡夫分別增字'),
 dict(ref=2, kind='誤報', reason='淫舍妓院增字'),
 dict(ref=3, kind='誤報', reason='末世凡愚加註'),
 dict(ref=2, kind='誤報', reason='浮囊喻語'),
 dict(ref=2, kind='誤報', reason='影響施化加註'),
 dict(ref=9, kind='誤報', reason='如前加註'),
 dict(ref=1, kind='誤報', reason='受隨同括注位置'),
 dict(ref=6, kind='誤報', reason='次第修捨增譯'),
]
B.make(N, items, verdicts)
