# -*- coding: utf-8 -*-
"""清除業疏原文與譯文中完全重複的段落（保留第一次出現）"""
import io, os, re, shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '03_業疏')
T = os.path.join(B, 'AI語譯', 'out', '03_業疏')
BAK = os.path.join(B, 'AI語譯', '_work', 'ys_dedup_bak')
os.makedirs(BAK, exist_ok=True)

changed = 0
removed = 0
for f in sorted(os.listdir(S)):
    if not f.endswith('.txt'):
        continue
    p = os.path.join(S, f)
    lines = io.open(p, encoding='utf-8').read().split('\n')
    head, body = lines[:5], [x for x in lines[5:] if x.strip()]
    seen = set()
    new = []
    for x in body:
        k = x.strip()
        if k in seen and len(k) < 40:      # 只去掉短重複（篇題一類）
            removed += 1
            continue
        seen.add(k)
        new.append(x)
    if len(new) != len(body):
        shutil.copyfile(p, os.path.join(BAK, 'sp_' + f))
        io.open(p, 'w', encoding='utf-8').write('\n'.join(head) + '\n' + '\n'.join(new) + '\n')
        changed += 1

changed_t = 0
for f in sorted(os.listdir(T)):
    if not f.endswith('.txt'):
        continue
    p = os.path.join(T, f)
    ps = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8').read()) if x.strip()]
    seen = set()
    new = []
    for x in ps:
        if x in seen and len(x) < 40:
            removed += 1
            continue
        seen.add(x)
        new.append(x)
    if len(new) != len(ps):
        shutil.copyfile(p, os.path.join(BAK, 'tt_' + f))
        io.open(p, 'w', encoding='utf-8').write('\n\n'.join(new) + '\n')
        changed_t += 1

print('原文檔修改', changed, '譯文檔修改', changed_t, '共移除', removed, '段')
