from docx import Document
import re, io, os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
d = Document(os.path.join(B, '白話', '會本_篇01_標宗顯德.docx'))
ps = [p.text.strip() for p in d.paragraphs]
seq = []
for t in ps:
    m = re.match(r'^【鈔(\d+)】', t)
    if m:
        seq.append(('c', int(m.group(1)))); continue
    m = re.match(r'^【記(\d+)】', t)
    if m:
        seq.append(('j', int(m.group(1))))
nums = [(i, x[1]) for i, x in enumerate(seq) if x[0] == 'j']
print('前 30:', nums[:30])
inv = [(a, b) for a, b in zip(nums, nums[1:]) if b[1] < a[1]]
print('逆序數', len(inv))
for a, b in inv[:6]:
    print(' 位置', a[0], '記', a[1], '→', b[1])
    for k in range(max(0, a[0] - 2), min(len(seq), b[0] + 2)):
        print('   ', seq[k])
