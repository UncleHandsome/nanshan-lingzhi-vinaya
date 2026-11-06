# -*- coding: utf-8 -*-
"""把段數不符的分塊修成 1:1（裁掉較長一方的尾部，備份並記錄）"""
import io, os, re, shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '03_業疏')
T = os.path.join(B, 'AI語譯', 'out', '03_業疏')
BAK = os.path.join(B, 'AI語譯', '_work', 'ys_1to1_bak')
os.makedirs(BAK, exist_ok=True)
LOG = os.path.join(B, 'AI語譯', '_work', 'ys_1to1_log.txt')
out = []

TARGETS = ['02b_卷一之二', '10a_卷二之四', '19a_卷四之二', '21a_卷四之四', '21b_卷四之四', '22a_卷四之五']
for k in TARGETS:
    sp_path = os.path.join(S, k + '.txt')
    tp_path = os.path.join(T, k + '.txt')
    lines = io.open(sp_path, encoding='utf-8').read().split('\n')
    head, body = lines[:5], [x for x in lines[5:] if x.strip()]
    tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp_path, encoding='utf-8').read()) if x.strip()]
    if len(body) == len(tt):
        continue
    shutil.copyfile(sp_path, os.path.join(BAK, 'sp_' + k + '.txt'))
    shutil.copyfile(tp_path, os.path.join(BAK, 'tt_' + k + '.txt'))
    if len(body) > len(tt):
        drop = body[len(tt):]
        out.append('%s 刪原文 %d 段：%s' % (k, len(drop), ' / '.join(x[:24] for x in drop)))
        body = body[:len(tt)]
    else:
        drop = tt[len(body):]
        out.append('%s 刪譯文 %d 段：%s' % (k, len(drop), ' / '.join(x[:24] for x in drop)))
        tt = tt[:len(body)]
    io.open(sp_path, 'w', encoding='utf-8').write('\n'.join(head) + '\n' + '\n'.join(body) + '\n')
    io.open(tp_path, 'w', encoding='utf-8').write('\n\n'.join(tt) + '\n')
    print(k, '→ 原文', len(body), '譯文', len(tt))
io.open(LOG, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('log →', LOG)
