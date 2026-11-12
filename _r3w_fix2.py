import sys
sys.path.insert(0, r'C:\Users\lionc\OneDrive\桌面\XW\三大部')
from _r3w_lib import *

# 181: 皆各各 -> 各各
book, chunk = '01_行事鈔', '08a_卷中之四'
text = read_text(book, chunk)
text = sub_para(text, 63, '皆各各加上不學與無知二罪', '各各加上不學與無知二罪', label='181-0003b')
save(text, book, chunk)

# 392: 重複違犯 -> 結犯 (two spots in #104)
book, chunk = '02_戒疏', '03b_卷一下之一'
text = read_text(book, chunk)
text = sub_para(text, 104, '有六種罪會在三處篇段中重複違犯', '有六種罪會在三處篇段中結犯', label='392-0001a')
text = sub_para(text, 104, '會在戒序以及七滅諍法這兩處重複違犯', '會在戒序以及七滅諍法這兩處問淨時結犯', label='392-0001b')
save(text, book, chunk)

# 472-0001: 自身卻親身踐履 -> 自身卻踐履
book, chunk = '02_戒疏', '05d_卷二上之一'
text = read_text(book, chunk)
text = sub_para(text, 138, '自身卻親身踐履非法惡行', '自身卻踐履非法惡行', label='472-0001c')
save(text, book, chunk)

# 551-0011: 銷釋律藏經文 -> 銷釋戒本經文
book, chunk = '02_戒疏', '09a_卷二下之二'
text = read_text(book, chunk)
text = sub_para(text, 126, '接著銷釋律藏經文時', '接著銷釋戒本經文時', label='551-0011b')
save(text, book, chunk)
print('cleanups done')
