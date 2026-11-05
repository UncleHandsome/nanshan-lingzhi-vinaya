import os, io, re, json, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RET = os.path.join(B, 'AI語譯', '_work', 'retr')
T = os.path.join(B, 'AI語譯', 'out', '02_戒疏')
LAY = json.load(io.open(os.path.join(B, 'AI語譯', 'layers', '02_戒疏.json'), encoding='utf-8'))
LAB = {'律': '律文', '註': '註文', '疏': '疏文', '記': '記文'}
LEAD = re.compile(r'^(【[^】]{1,6}】)+')


def main(write=False):
    got = {}
    for p in sorted(glob.glob(os.path.join(RET, 'out_*.json'))):
        arr = json.load(io.open(p, encoding='utf-8'))
        key = os.path.basename(p)[4:]
        for it in arr:
            # 找對應 key：批次檔為準
            got.setdefault(it.get('key') or '', {})
    # 重新以批次檔對應 key
    batches = {}
    for p in sorted(glob.glob(os.path.join(RET, '[0-9][0-9].json'))):
        meta = json.load(io.open(p, encoding='utf-8'))
        n = os.path.basename(p)[:2]
        batches[n] = meta['key']
    data = {}
    for p in sorted(glob.glob(os.path.join(RET, 'out_*.json'))):
        n = os.path.basename(p)[4:6]
        key = batches.get(n)
        if not key:
            print('!! 無法對應', p)
            continue
        arr = json.load(io.open(p, encoding='utf-8'))
        for it in arr:
            data.setdefault(key, {})[int(it['seg'])] = it['text'].strip()

    for key, d in data.items():
        ps = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(os.path.join(T, key + '.txt'), encoding='utf-8').read()) if x.strip()]
        lay = LAY.get(key, [])
        print('%-16s 得 %3d / 段數 %3d' % (key, len(d), len(ps)))
        if len(d) != len(ps) or not write:
            continue
        out = []
        for i in range(len(ps)):
            body = LEAD.sub('', d[i + 1]).strip()
            L = lay[i] if i < len(lay) else '記'
            out.append(('【' + LAB[L] + '】' + body) if L in LAB else body)
        io.open(os.path.join(T, key + '.txt'), 'w', encoding='utf-8').write('\n\n'.join(out) + '\n')
        print('  written', key)


if __name__ == '__main__':
    import sys
    main('--write' in sys.argv)
