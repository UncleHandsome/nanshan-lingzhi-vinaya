# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2e_build3 as B
N = 1750
items = [
 (1, '而將和尚視為輕賤', '和尚反而被他輕慢、不受尊重', '見輕為被動'),
 (4, '只要心中沒有渴求正法、攀緣境體之心', '只是說心中沒有渴仰戒法、緣念戒境之心', '但=只是'),
 (8, '文中敘述師弟法義教導興起的緣由', '文中先敘述師徒相待之義，以及制定請師之教的緣由', '師資教興'),
 (11, '正是制定請和尚的用意', '正是尊崇（和尚）而制此請師之法的用意（「可尚」二字疑有訛，待考）', '可尚制意'),
 (12, '陳朝真諦三藏所翻譯的《律二十二明了論疏》中', '陳朝真諦三藏所翻譯的《明了論疏》（即《律二十二明了論》之疏）中', '書名擅增'),
 (13, '所謂違背聲論，是因為前面所出的正確翻譯，乃是依據梵文聲明法則於譯場親自審定，名稱與意涵皆符合真實', '至於疏中說（真諦所譯）「乖聲論」：前面所出的正確譯名，乃是依聲明之學、並在譯場親自請問而得，所以名與義都能得其實', '乖聲論因果'),
 (13, '邊地西域是雜胡邊邦', '「蕃胡」是胡戎雜居的邊地之國', '蕃胡'),
 (3, '但結界處所並未成就而受者不知', '但對結界之事懵然不知（界相不明、成否未卜）', '界結不知'),
 (3, '不想念戒法的根本', '不繫念所受戒法之根本', '不念戒本'),
 (5, '第五項「事法成就同一」', '第五項「事成同一」', '科名照錄'),
 (7, '如律文所顯現的那樣', '如所釋《隨機羯磨》文所顯', '文=羯磨文'),
 (10, '若隨順煩惱墮落敗壞德行', '便隨之墮落、敗壞行持', '隨=隨之'),
 (9, '前半部分說明請師的緣由因致', '前半部分說明請師的緣由', '緣由因致贅'),
 (11, '是因儒教將人分為九等', '儒典將人分為九等', '因字為增'),
 (12, '我曾親自參與譯場', '（道宣說）我曾親自參與譯場', '餘為道宣自稱'),
]
verdicts = [
 dict(ref=1, kind='真錯', reason='和上見輕'),
 dict(ref=4, kind='真錯', reason='但=只是'),
 dict(ref=8, kind='真錯', reason='師資教興'),
 dict(ref=11, kind='真錯', reason='可尚制意'),
 dict(ref=12, kind='真錯', reason='書名'),
 dict(ref=13, kind='真錯', reason='乖聲論因果'),
 dict(ref=13, kind='真錯', reason='蕃胡'),
 dict(ref=3, kind='真錯', reason='界結不知'),
 dict(ref=3, kind='真錯', reason='不念戒本'),
 dict(ref=5, kind='真錯', reason='事成同一'),
 dict(ref=7, kind='真錯', reason='文=羯磨文'),
 dict(ref=10, kind='真錯', reason='隨墮'),
 dict(ref=9, kind='真錯', reason='緣由因致'),
 dict(ref=11, kind='真錯', reason='儒教因'),
 dict(ref=12, kind='真錯', reason='餘為自稱'),
 dict(ref=1, kind='誤報', reason='五大緣加註'),
 dict(ref=1, kind='誤報', reason='不名受'),
 dict(ref=2, kind='誤報', reason='承稟'),
 dict(ref=3, kind='誤報', reason='非緣不一'),
 dict(ref=3, kind='誤報', reason='引號白話'),
 dict(ref=4, kind='誤報', reason='翻上可明'),
 dict(ref=4, kind='誤報', reason='四句標籤'),
 dict(ref=5, kind='誤報', reason='五行加註'),
 dict(ref=6, kind='誤報', reason='正釋'),
 dict(ref=7, kind='誤報', reason='前緣列八'),
 dict(ref=10, kind='誤報', reason='中人已上加註'),
 dict(ref=12, kind='誤報', reason='唐譯言'),
 dict(ref=12, kind='誤報', reason='著名'),
]
B.make(N, items, verdicts)
