import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BOOKS = ['01_行事鈔', '02_戒疏', '03_業疏', '資持記_細分', '04_比丘尼鈔', '05_拾毗尼義鈔']


def fix_paras(ps):
    out = []
    open_ct = 0
    fixed = 0
    for s in ps:
        t = s
        if open_ct > 0 and t.startswith('〕'):
            t = t[1:]
            if t.startswith(('，', '。', '、', '；')):
                t = t[1:]
            open_ct -= 1
            fixed += 1
        open_ct += t.count('〔') - t.count('〕')
        if open_ct < 0:
            open_ct = 0
        out.append(t.strip())
    return out, fixed


def main(write=False):
    total = 0
    for sd in BOOKS:
        d = os.path.join(B, 'TXT_分卷', sd)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if not f.endswith('.txt'):
                continue
            p = os.path.join(d, f)
            raw = io.open(p, encoding='utf-8').read().split('\n')
            head, body = raw[:5], raw[5:]
            ps = [x for x in body if x.strip()]
            new, n = fix_paras(ps)
            if n:
                total += n
                if write:
                    io.open(p, 'w', encoding='utf-8').write('\n'.join(head) + '\n' + '\n'.join(new) + '\n')
                print('%s %-16s 修 %d' % (sd, f[:-4], n))
    print('total fixed', total)


if __name__ == '__main__':
    import sys
    main('--write' in sys.argv)
