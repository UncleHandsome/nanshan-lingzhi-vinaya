import sys
sys.path.insert(0, r'C:\Users\lionc\OneDrive\桌面\XW\三大部')
from _r3w_lib import *

book, chunk = '02_戒疏', '05a_卷二上之一'
text = read_text(book, chunk)
edits = [
 (108, '那就不在此常規限度之中了。', '那就不受前面那種說法的限制了（不可一概而論）。'),
 (112, '天界地位高遠，照理斷絕了相續不斷的欲心。', '天界地位高遠，照理說不會像下界那樣常存相續交染之心。'),
 (114, '那麼偷盜畜生與殺死畜生，罪名又為何一輕一重呢？', '那麼盜取畜生（所執受之物）與殺死畜生，罪名又為何一輕一重呢？'),
 (118, '這只是藉由譬喻，以輕微之物來反襯嚴重之情罷了。', '這只是借用譬喻，以輕微之事來比況重大之情（舉輕況重）罷了。'),
 (123, '對其欺誑根本無人相信，所以只制輕罪。', '對其欺誑根本無法令其信受（天人絕不會信以為真），所以只制輕罪。'),
]
for idx, old, new in edits:
    text = sub_para(text, idx, old, new, label=f'441#{idx}')
backup(book, chunk); save(text, book, chunk)
print('441 saved')
