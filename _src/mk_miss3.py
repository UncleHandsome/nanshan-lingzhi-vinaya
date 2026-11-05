import os, io, re, json, difflib

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '資持記_細分')
T = os.path.join(B, 'AI語譯', 'out', '資持記')
OUT = os.path.join(B, 'AI語譯', '_work', 'miss3')
SIZE = 30

han = lambda s: ''.join(c for c in s if '\u4e00' <= c <= '\u9fff')


def main():
    items = []
    for f in sorted(os.listdir(S)):
        if not f.endswith('.txt'):
            continue
        key = f[:-4]
        sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tp = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(os.path.join(T, key + '.txt'), encoding='utf-8').read()) if x.strip()]
        for i in range(min(len(sp), len(tp))):
            a, b = sp[i], tp[i]
            if han(a) and a == b and len(han(a)) > 20:
                items.append(dict(key=key, seg=i + 1, src=a))
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        os.remove(os.path.join(OUT, f))
    n = 0
    for i in range(0, len(items), SIZE):
        n += 1
        part = items[i:i + SIZE]
        io.open(os.path.join(OUT, '%02d.json' % n), 'w', encoding='utf-8').write(
            json.dumps(dict(items=part), ensure_ascii=False, indent=1))
        print('%02d %2d 段 (%s)' % (n, len(part), part[0]['key']))
    print('total', len(items), 'batches', n)


if __name__ == '__main__':
    main()
