# -*- coding: utf-8 -*-
"""把待補譯段落切成批次檔（_work/misstr/NN.json），供翻譯代理讀取。"""
import os, io, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, 'AI語譯', '_work', 'miss_input.json')
OUT = os.path.join(B, 'AI語譯', '_work', 'misstr')


def main():
    data = json.load(io.open(SRC, encoding='utf-8'))
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        os.remove(os.path.join(OUT, f))
    batches = []
    for entry in data:
        segs = entry['segs']
        key = entry['key']
        size = 40 if len(segs) > 60 else 999
        for i in range(0, len(segs), size):
            part = segs[i:i + size]
            batches.append(dict(book=entry['book'], key=key, segs=part))
            print('%-14s %-18s %3d 段' % (entry['book'], key, len(part)))
    for n, b in enumerate(batches, 1):
        io.open(os.path.join(OUT, '%02d.json' % n), 'w', encoding='utf-8').write(json.dumps(b, ensure_ascii=False, indent=1))
    print('batches', len(batches), 'segs', sum(len(b['segs']) for b in batches))


if __name__ == '__main__':
    main()
