# -*- coding: utf-8 -*-
"""篇為單位、鈔記交錯的校閱批次（v2）。

與 v1 的差別：v1 按 chunk 出檔，鈔檔沒有記、記檔沒有鈔；v2 依照會本的
「鈔→記」交錯順序輸出，校閱者看到的是同一段的鈔文與記文。

用法：
    python _src/review_batch2.py              # 全部 30 篇
    python _src/review_batch2.py --pian 23    # 只出篇23

輸出：
    AI語譯/_work/review/in2/篇NN_AAA-BBB.txt
    AI語譯/_work/review/manifest2.tsv
"""
import os, io, re, sys, glob, json, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)

IN = os.path.join(B, 'AI語譯', '_work', 'review', 'in2')
BD = os.path.join(B, 'AI語譯', '_work', 'pian_bounds')
PER = 25          # 每批段數


def index_book(srcdir):
    d = {}
    for f in sorted(glob.glob(os.path.join(B, 'TXT_分卷', srcdir, '*.txt'))):
        chunk = os.path.splitext(os.path.basename(f))[0]
        for i, x in enumerate([y.strip() for y in io.open(f, encoding='utf-8').read().split('\n')[5:] if y.strip()], 1):
            d.setdefault(x, (chunk, i))
    return d


def load_bounds(p):
    fp = os.path.join(BD, 'bounds_篇%02d.json' % p)
    if not os.path.exists(fp):
        return {}
    try:
        bs = [(int(x['c']), int(x['n'])) for x in json.load(io.open(fp, encoding='utf-8-sig'))['bounds']]
    except Exception:
        return {}
    return dict(bs)


def sequence(p, S, Z):
    """回傳 [(kind, idx)]：依會本順序交錯的鈔段與記段（1 起算）。"""
    M, N = len(S[p]['items']), len(Z[p])
    bm = load_bounds(p + 1)
    seq, prev = [], 0
    for c in range(1, M + 1):
        seq.append(('鈔', c))
        n = bm.get(c)
        if n is not None:
            for k in range(prev + 1, min(n, N) + 1):
                seq.append(('記', k))
            prev = max(prev, min(n, N))
    for k in range(prev + 1, N + 1):
        seq.append(('記', k))
    return seq


def main():
    args = sys.argv[1:]
    only = None
    if '--pian' in args:
        only = int(args[args.index('--pian') + 1])

    S = ex.sections()
    Z = ex.build_zi(S, ex.zsecs())
    IX = {'鈔': index_book('01_行事鈔'), '記': index_book('資持記_細分')}
    os.makedirs(IN, exist_ok=True)
    rows, unmapped = [], 0

    for p in range(len(S)):
        if only and p + 1 != only:
            continue
        seq = sequence(p, S, Z)
        items = []
        for kind, k in seq:
            orig, trans = (S[p]['items'][k - 1] if kind == '鈔' else Z[p][k - 1])
            ref = IX[kind].get(orig)
            if ref:
                tag = '%s/%s#%d' % (kind, ref[0], ref[1])
            else:
                tag = '%s/?#' % kind
                unmapped += 1
            items.append((kind, tag, orig, trans))

        name = '篇%02d' % (p + 1)
        for a in range(0, len(items), PER):
            b = min(a + PER, len(items))
            path = os.path.join(IN, '%s_%03d-%03d.txt' % (name, a + 1, b))
            out = ['# 校閱批次（鈔記對讀）',
                   '篇：%s　本批：%d–%d／%d 段' % (name, a + 1, b, len(items)),
                   '（每段先給原文、再給譯文；段末標出來源，供回報定位）', '']
            for i in range(a, b):
                kind, tag, orig, trans = items[i]
                out.append('【段%03d】%s' % (i + 1, tag))
                out.append('【原文】%s' % orig)
                out.append('【譯文】%s' % trans)
                out.append('')
            io.open(path, 'w', encoding='utf-8').write('\n'.join(out))
            rows.append((name, a + 1, b, b - a, sum(len(x[2]) + len(x[3]) for x in items[a:b]), os.path.basename(path)))

    man = os.path.join(B, 'AI語譯', '_work', 'review', 'manifest2.tsv')
    with io.open(man, 'w', encoding='utf-8') as fh:
        fh.write('pian\tfrom\tto\tsegs\tchars\tfile\n')
        for r in rows:
            fh.write('\t'.join(map(str, r)) + '\n')
    print('批次', len(rows), '段', sum(r[3] for r in rows), '未定位', unmapped)
    print('→', man)


if __name__ == '__main__':
    main()
