import os, io, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, 'AI語譯', '_work', 'untranslated.json')
OUT = os.path.join(B, 'AI語譯', '_work', 'miss2')
SIZE = 25


def main():
    data = json.load(io.open(SRC, encoding='utf-8'))
    rows = []
    for b in data:
        if b['tag'] == '02_戒疏':
            rows = b['rows']
    items = [dict(key=r['key'], seg=r['seg'], src=r['src']) for r in rows]
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        os.remove(os.path.join(OUT, f))
    n = 0
    for i in range(0, len(items), SIZE):
        n += 1
        part = items[i:i + SIZE]
        io.open(os.path.join(OUT, '%02d.json' % n), 'w', encoding='utf-8').write(
            json.dumps(dict(items=part), ensure_ascii=False, indent=1))
        print('%02d %2d 段 (%s…)' % (n, len(part), part[0]['key']))
    print('batches', n, 'segs', len(items))


if __name__ == '__main__':
    main()
