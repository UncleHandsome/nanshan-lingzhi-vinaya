# -*- coding: utf-8 -*-
"""稽核 r2 處理進度：哪些 resp 檔已有結果、哪些已登記處理、哪些漏掉。"""
import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
R2 = os.path.join(B, 'batch_qwen', 'r2')
DONE = os.path.join(B, 'batch_qwen', 'r2_done.txt')

have = sorted(int(re.search(r'resp_(\d+)', f).group(1))
              for f in os.listdir(R2) if f.startswith('resp_') and f.endswith('.txt'))

done = set()
for line in io.open(DONE, encoding='utf-8'):
    line = line.strip()
    m = re.match(r'^(\d+)-(\d+)$', line)
    if m:
        done |= set(range(int(m.group(1)), int(m.group(2)) + 1))
        continue
    for n in re.findall(r'\d+', line.replace('-', ' ')):
        done.add(int(n))

print('回覆檔數', len(have), '（%d–%d）' % (min(have), max(have)))
missing = [n for n in have if n not in done]
print('已登記處理', len([n for n in have if n in done]))
print('有結果但未登記', len(missing))
if missing:
    # 連續區間
    runs = []
    s = p = missing[0]
    for n in missing[1:]:
        if n == p + 1:
            p = n
        else:
            runs.append((s, p)); s = p = n
    runs.append((s, p))
    print('未登記區間：', ', '.join('%d-%d' % r if r[0] != r[1] else str(r[0]) for r in runs[:40]))
print('已登記但無結果', sorted(done - set(have))[:20])
