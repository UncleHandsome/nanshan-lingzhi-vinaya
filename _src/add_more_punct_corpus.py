# -*- coding: utf-8 -*-
import io, os, shutil
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, 'TXT_句讀校定')
os.makedirs(OUT, exist_ok=True)
for book, src in [('xingshichao', 'TXT/01_四分律刪繁補闕行事鈔.txt'),
                  ('jieshu', 'TXT/02_四分律含注戒本疏.txt')]:
    shutil.copy(os.path.join(B, src), os.path.join(OUT, book + '.txt'))
D = os.path.join(B, 'TXT_分卷', '資持記_細分')
parts = [io.open(os.path.join(D, f), encoding='utf-8').read() for f in sorted(os.listdir(D)) if f.endswith('.txt')]
io.open(os.path.join(OUT, 'zhichi.txt'), 'w', encoding='utf-8').write('\n\n'.join(parts))
print('written', [f for f in os.listdir(OUT) if f.endswith('.txt')])
