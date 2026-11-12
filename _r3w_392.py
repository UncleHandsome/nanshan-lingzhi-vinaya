import sys
sys.path.insert(0, r'C:\Users\lionc\OneDrive\桌面\XW\三大部')
from _r3w_lib import *

book, chunk = '02_戒疏', '03b_卷一下之一'
text = read_text(book, chunk)
edits = [
 (104, '這八種罪，各自會在當篇本戒、二不定法以及最初戒序這三處重複違犯。',
       '這八種罪，各自會在當篇本戒、二不定法以及最初戒序這三處問淨時結犯（默妄之罪）。'),
 (105, '在一處發露，所有重犯皆消除，不必在三處重複懺除。',
       '只要在一處發露，三處所結的罪便一併消滅，不必在三處分別懺除。'),
 (111, '因為唯有犯戒之人，才是被禁止聽聞戒律的。',
       '因為只要有犯戒的人，便不合聽聞戒法之故。'),
 (115, '隨有解悟，即須發露', '隨著省察而覺知自己有犯，便須立刻發露'),
 (117, '略教固然可說有戒相，但比丘尼律與法聚犍度',
       '說戒時宣讀七佛略教，說為了聽聞略教而問淨固然講得通；但比丘尼律與法聚犍度'),
]
for idx, old, new in edits:
    text = sub_para(text, idx, old, new, label=f'392#{idx}')
backup(book, chunk); save(text, book, chunk)
print('392 saved')
