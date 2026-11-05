import os, io, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '02_戒疏')
OUT = os.path.join(B, 'AI語譯', '_work', 'retr')
KEYS = ['18b_卷四上之三', '19b_卷四下之一']
SIZE = 48


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        os.remove(os.path.join(OUT, f))
    n = 0
    for key in KEYS:
        sp = [x.strip() for x in io.open(os.path.join(S, key + '.txt'), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        for i in range(0, len(sp), SIZE):
            n += 1
            part = [dict(seg=j + 1, src=sp[j]) for j in range(i, min(i + SIZE, len(sp)))]
            io.open(os.path.join(OUT, '%02d.json' % n), 'w', encoding='utf-8').write(
                json.dumps(dict(key=key, items=part), ensure_ascii=False, indent=1))
            print('%02d %-16s seg %d-%d' % (n, key, part[0]['seg'], part[-1]['seg']))
    print('batches', n)


if __name__ == '__main__':
    main()
