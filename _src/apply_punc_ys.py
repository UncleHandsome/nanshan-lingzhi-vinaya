import os, io, re, json, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
J = os.path.join(B, 'TXT_句讀', '03_業疏')
SRC = os.path.join(B, 'AI語譯', '_work', 'punc_ys')
han = lambda s: ''.join(c for c in s if '\u4e00' <= c <= '\u9fff')


def main(write=False):
    data = {}
    for p in sorted(glob.glob(os.path.join(SRC, 'out_*.json'))):
        for it in json.load(io.open(p, encoding='utf-8')):
            data.setdefault(it['file'], {})[int(it['line'])] = it['text'].strip()
    ok = bad = 0
    for f, d in data.items():
        p = os.path.join(J, f)
        ls = io.open(p, encoding='utf-8').read().split('\n')
        changed = False
        for i, t in d.items():
            if not (0 <= i < len(ls)):
                print('  越界', f, i); bad += 1; continue
            if han(ls[i]) != han(t):
                print('  內容不符', f, i, ls[i][:20], '|', t[:20]); bad += 1; continue
            if ls[i].strip() != t:
                ls[i] = t
                changed = True
                ok += 1
        if changed and write:
            io.open(p, 'w', encoding='utf-8').write('\n'.join(ls))
    print('updated', ok, 'rejected', bad)


if __name__ == '__main__':
    import sys
    main('--write' in sys.argv)
