# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2e_build3 as B
N = 1757
items = [
 (2, '準則有四句', '按理推準，共有四句', '準=推準'),
 (1, '如同造作四重戒', '例如犯了四重（四波羅夷）', '造=違犯'),
 (1, '都會產生混濫', '都有繁雜或混濫的過失', '繁濫'),
 (1, '或者杖打父母等尊長', '或者毆打、棒打父母等尊長', '打棒'),
 (1, '例如殺害三代祖先乃至繼母等', '例如殺害祖、曾祖、高祖乃至繼母等', '三祖'),
 (3, '並非依照罪行輕重來區分，因為兩者都是在眾僧法中造作的緣故', '並非就「二重」再分成二難，因為這二重都是共作僧眾之法的緣故', '不從重分/眾別'),
 (15, '無法透過等待延期來除滅', '不能靠等待時日或改易去除而消失', '延除二義'),
 (15, '所以只在「遮障」中收攝', '所以只歸在「遮（遮法）」中收攝', '遮非遮障'),
 (11, '是隱匿事相而顯明法義', '是隱去（不別列）具體罪相而顯明法義', '隱相'),
 (11, '受具足戒與受未具足戒者', '受具足戒者與未受具足戒者（但受五戒、八戒、十戒者）', '具不具語病'),
 (8, '首先依據名稱之中', '先約名稱辨釋（這一科）中：', '科文不成句'),
 (13, '其次在諍論名稱之中', '其次、辨諍名稱（這一科）中：', '科文不成句'),
 (12, '這與壞比丘尼相同', '這與壞比丘尼相同（原文作「壞凡」，疑為「壞尼」之訛）', '壞凡校註'),
 (5, '又有一種解釋：五逆如果合而不分', '第三師又說：五逆如果合而不分', '第三師'),
]
verdicts = [
 dict(ref=2, kind='真錯', reason='準'),
 dict(ref=1, kind='真錯', reason='造四重'),
 dict(ref=1, kind='真錯', reason='皆有濫'),
 dict(ref=1, kind='真錯', reason='打棒'),
 dict(ref=1, kind='真錯', reason='三祖'),
 dict(ref=3, kind='真錯', reason='不從重分'),
 dict(ref=15, kind='真錯', reason='延除'),
 dict(ref=15, kind='真錯', reason='遮收'),
 dict(ref=11, kind='真錯', reason='隱相'),
 dict(ref=11, kind='真錯', reason='具不具'),
 dict(ref=8, kind='真錯', reason='先據名'),
 dict(ref=13, kind='真錯', reason='次諍名'),
 dict(ref=12, kind='真錯', reason='壞凡'),
 dict(ref=5, kind='真錯', reason='第三師'),
 dict(ref=1, kind='誤報', reason='今分為四'),
 dict(ref=1, kind='誤報', reason='戒障簡輕'),
 dict(ref=2, kind='誤報', reason='忤逆/惡逆'),
 dict(ref=3, kind='誤報', reason='只共說戒'),
 dict(ref=4, kind='誤報', reason='釋之可解'),
 dict(ref=11, kind='誤報', reason='四戒加註'),
 dict(ref=12, kind='誤報', reason='今所取'),
 dict(ref=16, kind='誤報', reason='反初義/反次義'),
]
B.make(N, items, verdicts)
