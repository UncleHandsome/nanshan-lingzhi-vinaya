
# -*- coding: utf-8 -*-
import io, re, os
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = os.path.join(D, '04_四分律比丘尼鈔_句讀_v2.txt')
t = io.open(p, encoding='utf-8').read()
# 切掉開頭對話殘留，從書名開始
i = t.find('四分律比丘尼鈔')
# 找「卷上」前的抬頭最穩：取第一次出現「四分律比丘尼鈔卷上」或「四分律比丘尼鈔」
j = t.find('四分律比丘尼鈔卷上')
start = j if j >= 0 else i
body = t[start:] if start >= 0 else t
# 去掉批次標題與 markdown 痕跡
body = re.sub(r'^#{1,6}.*$', '', body, flags=re.M)
body = re.sub(r'^\s*[-*]{3,}\s*$', '', body, flags=re.M)
body = body.replace('**', '')
body = re.sub(r'\n{3,}', '\n\n', body).strip()
io.open(os.path.join(D, '04_四分律比丘尼鈔_句讀_clean.txt'), 'w', encoding='utf-8').write(body + '\n')
print('clean chars', len(body))
print('head:', body[:80].replace('\n', ' '))
