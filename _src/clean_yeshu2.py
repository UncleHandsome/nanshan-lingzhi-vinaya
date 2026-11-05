
# -*- coding: utf-8 -*-
import io, os, re
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
t = io.open(os.path.join(D,'03_四分律刪補隨機羯磨疏_句讀_v3.txt'), encoding='utf-8').read()
# 找「四分律刪補隨機羯磨疏」後面接空白或 卷/序 的位置
cands = [m.start() for m in re.finditer(r'四分律刪補隨機羯磨疏', t)]
start = cands[-1] if cands else 0
for c in cands:
    tail = t[c:c+30]
    if re.search(r'[　\s]*(卷|序|曇無德)', tail) and c > 200:
        start = c; break
body = t[start:]
body = re.sub(r'^#{1,6}.*$', '', body, flags=re.M)
body = re.sub(r'^\s*[-*]{3,}\s*$', '', body, flags=re.M)
body = body.replace('**', '')
body = re.sub(r'\n{3,}', '\n\n', body).strip()
io.open(os.path.join(D,'03_四分律刪補隨機羯磨疏_句讀_clean.txt'),'w',encoding='utf-8').write(body+'\n')
han = len(re.findall(r'[\u4e00-\u9fff]', body))
punct = len(re.findall(r'[。，、；：？！]', body))
print('start', start, 'chars', len(body), 'han', han, 'density %.1f' % (1000.0*punct/max(1,han)))
print(body[:60].replace('\n',' '))
