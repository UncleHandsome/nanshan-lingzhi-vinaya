import os, io, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
J = os.path.join(B, 'TXT_句讀', '03_業疏')
OUT = os.path.join(B, 'AI語譯', '_work', 'punc_ys')
han = lambda s: ''.join(c for c in s if '\u4e00' <= c <= '\u9fff')
SIZE = 12


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        os.remove(os.path.join(OUT, f))
    items = []
    for f in sorted(os.listdir(J)):
        if not f.endswith('.txt'):
            continue
        ls = io.open(os.path.join(J, f), encoding='utf-8').read().split('\n')
        for i, s in enumerate(ls):
            h = han(s)
            if len(h) < 20:
                continue
            d = sum(s.count(c) for c in '，。、；：？！') / max(1, len(h))
            if d < 0.02:
                items.append(dict(file=f, line=i, text=s.strip()))
    n = 0
    for i in range(0, len(items), SIZE):
        n += 1
        part = items[i:i + SIZE]
        io.open(os.path.join(OUT, '%02d.json' % n), 'w', encoding='utf-8').write(
            json.dumps(dict(items=part), ensure_ascii=False, indent=1))
        print('%02d %2d 段' % (n, len(part)))
    print('total', len(items), 'batches', n)


if __name__ == '__main__':
    main()
