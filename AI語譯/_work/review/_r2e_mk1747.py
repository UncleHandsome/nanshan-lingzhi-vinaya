# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2e_build3 as B
N = 1747
items = [
 (1, '先簡別其餘惡趣', '先簡別其餘諸趣，列示五道', '餘趣非惡趣'),
 (1, '「苦輕下趣」，是指沒有惡道恆常的劇苦', '「苦輕下趣」，是說人道之苦屬無常、間斷之苦（不似下趣恆受劇苦）', '無常苦'),
 (1, '是指沒有天界耽溺的勝境', '是指沒有天界那樣殊勝的樂境', '耽溺為增字'),
 (1, '在第一項「唯人道」中', '在第一項「人道」中', '科目無唯字'),
 (1, '是將阿修羅合並通攝於諸趣之故', '是將阿修羅合併通攝於諸趣之故', '合並→合併'),
 (4, '戒教通達末世流俗', '教法通被末世凡俗', '通=通被'),
 (7, '如文末指引廣論', '自「如」字以下是指引廣說', '如下=科判'),
 (7, '懇切敕令審慎斟量', '鄭重教誡，要審慎斟量', '敕令非疏主'),
 (11, '所以與戒體互為相違', '所以與受戒相違', '相違非互為'),
 (11, '然而依據構成遮難的條件', '依構成障難的條件', '難非遮'),
 (10, '所以納入遮難所攝', '所以攝歸「難」中', '難非遮'),
 (3, '是指青盲、黃眼、赤眼、白翳、爛瞼、紅眼、水晶眼、極深陷、三角眼、眼眶大張、斜視、瞋目、微梨眼（眼球震顫或畸形）等',
     '是指青眼、黃眼、赤眼、白眼、爛眼、紅眼、水精（水晶）眼、極深、三角、大張、斜、瞋、微梨等（「微梨」未詳，疑為眼病名）',
     '眼病名臆解'),
 (8, '容易染成如法的色澤', '容易染上顏色', '如法為增字'),
 (8, '都構成受戒的難事', '都是受戒的障難（十三難）', '戒難=障難'),
 (6, '都不能列入合格之數', '都不能算入僧數（不足數、不得充數）', '足數術語'),
]
verdicts = [
 dict(ref=1, kind='真錯', reason='餘趣'),
 dict(ref=1, kind='真錯', reason='無常苦'),
 dict(ref=1, kind='真錯', reason='樂劣上天'),
 dict(ref=1, kind='真錯', reason='唯人道'),
 dict(ref=1, kind='真錯', reason='合並'),
 dict(ref=4, kind='真錯', reason='教通末俗'),
 dict(ref=7, kind='真錯', reason='如下指廣'),
 dict(ref=7, kind='真錯', reason='敕令'),
 dict(ref=11, kind='真錯', reason='故與相違'),
 dict(ref=11, kind='真錯', reason='成難'),
 dict(ref=10, kind='真錯', reason='難攝'),
 dict(ref=3, kind='真錯', reason='眼病名'),
 dict(ref=8, kind='真錯', reason='易染'),
 dict(ref=8, kind='真錯', reason='戒難'),
 dict(ref=6, kind='真錯', reason='合格之數'),
 dict(ref=1, kind='誤報', reason='天須陀食'),
 dict(ref=1, kind='誤報', reason='百千伎樂'),
 dict(ref=2, kind='誤報', reason='僧倫重複'),
 dict(ref=2, kind='誤報', reason='悅動眾心'),
 dict(ref=6, kind='誤報', reason='有疑通決'),
 dict(ref=10, kind='誤報', reason='無戒可犯'),
 dict(ref=11, kind='誤報', reason='但若有賊住'),
 dict(ref=3, kind='誤報', reason='總列諸遮'),
 dict(ref=9, kind='誤報', reason='先法後喻'),
]
B.make(N, items, verdicts)
