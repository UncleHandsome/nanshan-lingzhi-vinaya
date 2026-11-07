import glob, os, io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))
lines = ['# 行事鈔 未譯／疑似未譯清單', '']
n_tot = 0
for f in sorted(glob.glob(os.path.join(B, 'TXT_分卷', '01_行事鈔', '*.txt'))):
    k = os.path.basename(f)[:-4]
    sp = [x.strip() for x in io.open(f, encoding='utf-8').read().split('\n')[5:] if x.strip()]
    tp = os.path.join(B, 'AI語譯', 'out', '01_行事鈔', k + '.txt')
    tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
    bad = []
    for i in range(min(len(sp), len(tt))):
        a, b = han(sp[i]), han(tt[i])
        if len(a) < 15:
            continue
        same = a[:20] == b[:20]
        plain = (a.count('，') + a.count('。')) > 3 and ('的' not in b and '是' not in b and '這' not in b and '了' not in b)
        if same or plain:
            bad.append((i + 1, sp[i][:40]))
    if bad:
        n_tot += len(bad)
        lines.append('## %s（%d 段）' % (k, len(bad)))
        for i, t in bad[:12]:
            lines.append('- 第%d段：%s' % (i, t))
        lines.append('')
lines.insert(2, '合計 %d 段' % n_tot)
io.open(os.path.join(B, '待重譯清單_行事鈔.md'), 'w', encoding='utf-8').write('\n'.join(lines))
print('flagged', n_tot)
