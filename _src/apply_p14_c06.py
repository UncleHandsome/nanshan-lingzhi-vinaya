import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
NEW = io.open(os.path.join(B, '_src', 'p14_c06.txt'), encoding='utf-8').read().strip()
k = '05a_卷中之一'
sp = [x.strip() for x in io.open(os.path.join(B, 'TXT_分卷', '01_行事鈔', k + '.txt'), encoding='utf-8').read().split('\n')[5:] if x.strip()]
tp = os.path.join(B, 'AI語譯', 'out', '01_行事鈔', k + '.txt')
tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
i = [j for j, s in enumerate(sp) if s.startswith('三略解名義')][0]
tt[i] = NEW
io.open(tp, 'w', encoding='utf-8').write('\n\n'.join(tt) + '\n')
print('已補 05a 第', i, '段（鈔06）')
