# -*- coding: utf-8 -*-
"""第二批補遺：02a 尾段 5 條（原文＋白話）"""
import io, os, re, shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '03_業疏')
T = os.path.join(B, 'AI語譯', 'out', '03_業疏')
BAK = os.path.join(B, 'AI語譯', '_work', 'ys_insert_bak')
os.makedirs(BAK, exist_ok=True)

k = '02a_卷一之二'
ADD = [
    ('【記】答中二：初約還財不定，答懺捨五人。一是所為懺主，身外三人非僧，所以懺主入四人攝，但是四人法耳。律中還財，諸長隔日，餘雖即座，然亦無在，故云「未必」也。又下次約受懺不同釋：懺主白時，外無人足，故自入數，與受全別。',
     '解答分為兩部分：首先是依據還財時間未定，來解答懺悔捨墮的五人中，其中一人是承受懺悔的主人；懺主身外的三人單獨不能成僧，因此懺主計入以湊足四人之數，這只不過是四人僧的法度罷了。律藏中歸還長財通常隔日進行，其餘捨墮物雖然當席即座歸還也無妨，所以說「未必如此」。其次，依據接受懺悔的不同情形來解釋：懺主宣告單白時，身外沒有其他足夠的人，所以自己計入人數，這與受戒的情形截然不同。'),
    ('【疏】問：法是僧秉，方名羯磨；今秉法者不入僧中，法非僧法。',
     '提問：佛法必須由僧伽來主持秉持，才稱得上是羯磨；如今主持羯磨的人既然不算在僧伽之內，那麼所行的法就不是僧伽之法了。'),
    ('【記】三問中，躡上戒師身外成僧，以明教意。',
     '第三段提問中，緊接著前面「戒師在自身之外另湊足僧數」的說法，以此來探討聖教的深意。'),
    ('【疏】答：前事委僧，僧法和問，義須進不；人雖非應，法為僧成，故所被事皆名僧法，如學悔秉法也。',
     '回答：先前的公事完全託付給僧伽，僧團的法度本來就是藉由和合相問來決定贊同或反對；懺悔者本人雖然不屬於僧團之列，但羯磨是由僧伽所成就的，所以被處理的事項全都可以稱為僧伽之法，就如同身受學悔之法者也能依律秉法一樣。'),
    ('【記】答中：律中說恣無能秉法，故開學悔自不預數，足為明準。',
     '解答中指出：律藏中規定說戒與自恣若無人能主持，便開許身負學悔罪的人去主持，但他自己並不計入成僧的人數，這足以作為明晰的準則。'),
]

sp_path = os.path.join(S, k + '.txt')
tp_path = os.path.join(T, k + '.txt')
lines = io.open(sp_path, encoding='utf-8').read().split('\n')
head, body = lines[:5], [x for x in lines[5:] if x.strip()]
ps = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp_path, encoding='utf-8').read()) if x.strip()]
shutil.copyfile(sp_path, os.path.join(BAK, 'sp_' + k + '_b2.txt'))
shutil.copyfile(tp_path, os.path.join(BAK, 'tt_' + k + '_b2.txt'))
pos = len(body)
for i, (o, t) in enumerate(ADD):
    body.insert(pos + i, o)
    ps.insert(pos + i, t)
io.open(sp_path, 'w', encoding='utf-8').write('\n'.join(head) + '\n' + '\n'.join(body) + '\n')
io.open(tp_path, 'w', encoding='utf-8').write('\n\n'.join(ps) + '\n')
print(k, '插入', len(ADD), '段 → 原文', len(body), '譯文', len(ps))
