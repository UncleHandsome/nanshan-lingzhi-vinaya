import sys
sys.path.insert(0, r'C:\Users\lionc\OneDrive\桌面\XW\三大部')
from _r3w_lib import *

# 472-0001 is in 05d_卷二上之一
book, chunk = '02_戒疏', '05d_卷二上之一'
text = read_text(book, chunk)
text = sub_para(text, 138, '自身行為卻深陷非理惡行之中，內心毫無慚愧之色', '自身卻親身踐履非法惡行，內心毫無慚愧之意', label='472-0001a')
text = sub_para(text, 138, '多在自心深處自我警惕警省', '多少警惕自己的內心（稍作自心的警省）', label='472-0001b')
backup(book, chunk); save(text, book, chunk)
print('472-0001 saved')

book, chunk = '02_戒疏', '06a_卷二上之二'
text = read_text(book, chunk)
edits = [
 (3, '所以戒律是一切因緣與戒條的根本', '所以戒律是犯戒起緣所歸的根本'),
 (3, '廣泛鋪展修行的實體', '廣泛鋪展戒行的體相'),
 (3, '所以經文說「想要說戒的人', '所以律文說「想要說戒的人'),
 (21, '「眾學」與「滅諍」兩篇僅單純列出持守的行相', '「眾學」與「七滅諍」兩篇僅單純列出持守的行相'),
 (21, '所以簡略而不逐條列出，這是可以理解明白的。', '所以把「比丘」等字省略而未標出，這是可以推知明白的。'),
 (22, '在貫通抉擇的段落中，第一句分為兩部分', '在貫通抉擇的段落中，解釋初句的疏文分為兩部分'),
 (22, '上面兩句說明文字上的缺漏', '上面兩句說明文字上的未予列載'),
]
for idx, old, new in edits:
    text = sub_para(text, idx, old, new, label=f'472#{idx}')
backup(book, chunk); save(text, book, chunk)
print('472 rest saved')
