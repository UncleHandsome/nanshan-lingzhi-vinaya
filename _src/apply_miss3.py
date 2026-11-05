import os, io, re, json, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, 'AI語譯', '_work', 'miss3')
T = os.path.join(B, 'AI語譯', 'out', '資持記')
LEAD = re.compile(r'^(【[^】]{1,6}】)+')


def main(write=False):
    got = {}
    for p in sorted(glob.glob(os.path.join(SRC, 'out_*.json'))):
        for it in json.load(io.open(p, encoding='utf-8')):
            got.setdefault(it['key'], {})[int(it['seg'])] = it['text'].strip()
    total = 0
    for key, d in got.items():
        p = os.path.join(T, key + '.txt')
        ps = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8').read()) if x.strip()]
        bad = [s for s in d if not (1 <= s <= len(ps))]
        print('%-16s 得 %3d / 段 %3d 越界 %s' % (key, len(d), len(ps), bad[:3]))
        if bad or not write:
            continue
        for s, txt in d.items():
            body = LEAD.sub('', txt).strip()
            m = LEAD.match(ps[s - 1])
            ps[s - 1] = (m.group(0) + body) if m else body
        io.open(p, 'w', encoding='utf-8').write('\n\n'.join(ps) + '\n')
        total += len(d)
    print('written', total)


if __name__ == '__main__':
    import sys
    main('--write' in sys.argv)
