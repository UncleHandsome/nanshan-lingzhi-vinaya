import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
fp = os.path.join(B, 'AI語譯', 'out', '01_行事鈔', '05a_卷中之一.txt')
sp = [x.strip() for x in io.open(os.path.join(B, 'TXT_分卷', '01_行事鈔', '05a_卷中之一.txt'), encoding='utf-8').read().split('\n')[5:] if x.strip()]
tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(fp, encoding='utf-8').read()) if x.strip()]
K = 17  # 三者偷蘭遮 的位置
assert sp[K].startswith('三者偷蘭遮'), sp[K][:20]
new = tt[:K] + tt[K + 1:] + [tt[-1]]
io.open(fp, 'w', encoding='utf-8').write('\n\n'.join(new) + '\n')
print('05a 由第 17 段起左移一格；len', len(new))
for i in (16, 17, 18, 19):
    print(i, sp[i][:12], '||', new[i][:28])
