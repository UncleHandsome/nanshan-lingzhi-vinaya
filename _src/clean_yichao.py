
# -*- coding: utf-8 -*-
import io, re, os
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
VAR = {'牀':'床','説':'說','衆':'眾','爲':'為','敎':'教','卽':'即','旣':'既','竝':'並'}
def han(s): return ''.join(VAR.get(ch, ch) for ch in s if '\u4e00' <= ch <= '\u9fff' or ch == '〇')
t = io.open(os.path.join(D,'05_四分律拾毗尼義鈔_句讀_v2.txt'), encoding='utf-8').read()
j = t.find('四分律拾毗尼義鈔')
body = t[j:] if j >= 0 else t
body = re.sub(r'^#{1,6}.*$', '', body, flags=re.M)
body = re.sub(r'^\s*[-*]{3,}\s*$', '', body, flags=re.M)
body = body.replace('**', '')
body = re.sub(r'\n{3,}', '\n\n', body).strip()
io.open(os.path.join(D,'05_四分律拾毗尼義鈔_句讀_clean.txt'),'w',encoding='utf-8').write(body + '\n')
src = han(io.open(os.path.join(D,'TXT','05_四分律拾毗尼義鈔.txt'), encoding='utf-8').read())
ju = han(body)
k = 12
jush = set(ju[i:i+k] for i in range(len(ju)-k))
tot = len(src)//k
miss = [i for i in range(0, len(src)-k, k) if src[i:i+k] not in jush]
print('clean chars', len(body), 'coverage %.2f%%' % (100.0*(1-len(miss)*1.0/tot)), 'miss segs', len(miss))
