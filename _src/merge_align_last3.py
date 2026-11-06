import io, os, glob, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_last3')
TARGET = os.path.join(B, 'AI語譯', '_work', 'hb_align.json')

main = json.load(io.open(TARGET, encoding='utf-8'))
added = {}
for bf in sorted(glob.glob(os.path.join(AD, '[0-9][0-9][0-9].json'))):
    n = os.path.basename(bf)[:3]
    of = os.path.join(AD, 'out_%s.json' % n)
    if not os.path.exists(of):
        print('missing', n)
        continue
    meta = json.load(io.open(bf, encoding='utf-8-sig'))
    sec = meta['sec']
    d = json.load(io.open(of, encoding='utf-8-sig'))
    arr = {}
    for m in d.get('map', []):
        arr[int(m['z'])] = int(m['c'])
    if not arr:
        continue
    mx = max(arr) + 1
    seq, last = [], 0
    for i in range(mx):
        last = max(last, arr.get(i, last))
        seq.append(last)
    main[str(sec - 1)] = seq
    added[sec] = len(seq)
json.dump(main, io.open(TARGET, 'w', encoding='utf-8'), ensure_ascii=False)
print('merged', added, 'now 篇', len(main), '記段', sum(len(v) for v in main.values()))
