import os, io, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, 'AI語譯', '_work', 'untranslated.json')
OUT = os.path.join(B, 'AI語譯', '_work', 'miss4')
SIZE = 20


def main():
    data = json.load(io.open(SRC, encoding='utf-8'))
    items = []
    for b in data:
        if b['tag'] not in ('01_行事鈔', '資持記'):
            continue
        for r in b['rows']:
            items.append(dict(tag=b['tag'], key=r['key'], seg=r['seg'], src=r['src']))
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        os.remove(os.path.join(OUT, f))
    n = 0
    for i in range(0, len(items), SIZE):
        n += 1
        part = items[i:i + SIZE]
        io.open(os.path.join(OUT, '%02d.json' % n), 'w', encoding='utf-8').write(
            json.dumps(dict(items=part), ensure_ascii=False, indent=1))
        print('%02d %2d 段 %s' % (n, len(part), part[0]['key']))
    print('total', len(items), 'batches', n)


if __name__ == '__main__':
    main()
