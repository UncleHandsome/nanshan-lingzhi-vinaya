import glob, os, re
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
for f in sorted(glob.glob(os.path.join(B, '白話', '會本_篇*.docx'))):
    base = os.path.basename(f)
    m = re.search(r'篇(\d+)', base)
    if not m or int(m.group(1)) < 11:
        continue
    d = Document(f)
    ps = [p.text.strip() for p in d.paragraphs]
    seq = [(mm.group(1), int(mm.group(2))) for t in ps for mm in [re.match(r'^【(鈔|記)(\d+)', t)] if mm]
    inv = 0
    last = 0
    for tag, n in seq:
        if tag == '記':
            if n < last:
                inv += 1
            last = max(last, n)
    chao = [n for t, n in seq if t == '鈔']
    noji = [c for c in chao if not any(t == '記' and False for t, n in seq)]
    # 無記鈔：該鈔之後到下一個鈔之前沒有記
    idx = [i for i, (t, n) in enumerate(seq) if t == '鈔']
    empty = []
    for k, i in enumerate(idx):
        j = idx[k + 1] if k + 1 < len(idx) else len(seq)
        if not any(seq[x][0] == '記' for x in range(i + 1, j)):
            empty.append(seq[i][1])
    blank = sum(1 for i, t in enumerate(ps) if re.match(r'^【記', t) and (i + 1 >= len(ps) or len(ps[i + 1]) < 6))
    print('%-22s 鈔%3d 記片%3d 逆序%2d 無記鈔%s 空譯%d' % (base[:-5], len(chao), sum(1 for t, n in seq if t == '記'), inv, empty[:6], blank))
