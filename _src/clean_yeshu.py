
# -*- coding: utf-8 -*-
import io, os, re
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
t = io.open(os.path.join(D,'03_四分律刪補隨機羯磨疏_句讀_v3.txt'), encoding='utf-8').read()
i = t.find('四分律刪補隨機羯磨疏')
body = t[i:] if i > 0 else t
body = re.sub(r'^#{1,6}.*$', '', body, flags=re.M)
body = re.sub(r'^\s*[-*]{3,}\s*$', '', body, flags=re.M)
body = body.replace('**', '')
body = re.sub(r'\n{3,}', '\n\n', body).strip()
io.open(os.path.join(D,'03_四分律刪補隨機羯磨疏_句讀_clean.txt'),'w',encoding='utf-8').write(body+'\n')
punct = len(re.findall(r'[。，、；：？！「」『』（）〔〕《》]', body))
han = len(re.findall(r'[\u4e00-\u9fff]', body))
print('clean chars', len(body), 'han', han, 'density %.1f‰' % (1000.0*punct/max(1,han)))
