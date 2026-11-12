import sys
sys.path.insert(0, r'C:\Users\lionc\OneDrive\桌面\XW\三大部')
from _r3w_lib import *

book, chunk = '02_戒疏', '05b_卷二上之一'
text = read_text(book, chunk)
edits = [
 (51, '引用經文證明的段落中', '引用律文證明的段落中'),
 (52, '並不能直接斷除內在自性中的煩惱妄惑', '並不能直接斷除內在心性根本的煩惱妄惑'),
 (62, '第一門，他人見解的第一個科判中。', '在前一門（明先後次第門）中，引述他人見解的第一個科判裡。'),
]
for idx, old, new in edits:
    text = sub_para(text, idx, old, new, label=f'448#{idx}')
backup(book, chunk); save(text, book, chunk)
print('448 saved')
