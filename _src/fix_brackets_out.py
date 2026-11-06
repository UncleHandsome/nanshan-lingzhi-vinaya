import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BOOKS = ['01_行事鈔', '02_戒疏', '03_業疏', '資持記', '04_比丘尼鈔', '05_拾毗尼義鈔']


def fix_paras(ps):
    out, open_ct, n = [], 0, 0
    for s in ps:
        t = s
        if open_ct > 0 and t.lstrip().startswith('〕'):
            t = t.lstrip()[1:]
            if t.startswith(('，', '。', '、', '；')):
                t = t[1:]
            open_ct -= 1
            n += 1
        open_ct += t.count('〔') - t.count('〕')
        if open_ct < 0:
            open_ct = 0
        out.append(t.strip())
    return out, n


total = 0
for tag in BOOKS:
    d = os.path.join(B, 'AI語譯', 'out', tag)
    if not os.path.isdir(d):
        continue
    for f in sorted(os.listdir(d)):
        if not f.endswith('.txt'):
            continue
        p = os.path.join(d, f)
        ps = [x for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8').read()) if x.strip()]
        new, n = fix_paras(ps)
        if n:
            io.open(p, 'w', encoding='utf-8').write('\n\n'.join(new) + '\n')
            total += n
            print(tag, f[:-4], n)
print('fixed', total)
