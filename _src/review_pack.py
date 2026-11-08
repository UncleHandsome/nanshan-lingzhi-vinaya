# -*- coding: utf-8 -*-
"""把校閱材料打包成每檔約 65KB 的批次（不再按 chunk 細切）。

用法：
    python _src/review_pack.py                 # 預設 65000 bytes
    python _src/review_pack.py --size 65000

輸出：
    AI語譯/_work/review/pack/in/校閱_01.txt …（連續編號）
    AI語譯/_work/review/pack/index.tsv

排序：先「鈔記對讀」（行事鈔＋資持記，依會本篇序），再戒疏、業疏、尼鈔、尼義鈔。
段號在每個檔內連續（1 起算），每段附來源 book/chunk#seg。
"""
import os, io, re, sys, glob, json, importlib.util

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, 'AI語譯', '_work', 'review', 'pack', 'in')
BD = os.path.join(B, 'AI語譯', '_work', 'pian_bounds')

spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)


def src_paras(book, chunk):
    d = {'01_行事鈔': '01_行事鈔', '02_戒疏': '02_戒疏', '03_業疏': '03_業疏',
         '資持記': '資持記_細分', '04_比丘尼鈔': '04_比丘尼鈔', '05_拾毗尼義鈔': '05_拾毗尼義鈔'}
    p = os.path.join(B, 'TXT_分卷', d[book], chunk + '.txt')
    return [x.strip() for x in io.open(p, encoding='utf-8').read().split('\n')[5:] if x.strip()]


def tr_paras(book, chunk):
    p = os.path.join(B, 'AI語譯', 'out', book, chunk + '.txt')
    return [x for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8').read()) if x.strip()]


def bounds(p):
    fp = os.path.join(BD, 'bounds_篇%02d.json' % p)
    if not os.path.exists(fp):
        return {}
    try:
        return dict((int(x['c']), int(x['n'])) for x in json.load(io.open(fp, encoding='utf-8-sig'))['bounds'])
    except Exception:
        return {}


def sequence(p, S, Z):
    M, N = len(S[p]['items']), len(Z[p])
    bm = bounds(p + 1)
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


def maoji_items():
    S = ex.sections()
    Z = ex.build_zi(S, ex.zsecs())
    idx = {}
    for tag, sd in (('鈔', '01_行事鈔'), ('記', '資持記_細分')):
        for f in sorted(glob.glob(os.path.join(B, 'TXT_分卷', sd, '*.txt'))):
            ch = os.path.splitext(os.path.basename(f))[0]
            for i, x in enumerate([y.strip() for y in io.open(f, encoding='utf-8').read().split('\n')[5:] if y.strip()], 1):
                idx.setdefault((tag, x), (ch, i))
    books = {'鈔': '01_行事鈔', '記': '資持記'}
    items = []
    for p in range(len(S)):
        for kind, k in sequence(p, S, Z):
            orig, trans = (S[p]['items'][k - 1] if kind == '鈔' else Z[p][k - 1])
            ref = idx.get((kind, orig))
            if not ref:
                continue
            book = books[kind]
            items.append((book, ref[0], ref[1], orig, trans))
    return items


def book_items(book, srcdir):
    items = []
    for f in sorted(glob.glob(os.path.join(B, 'TXT_分卷', srcdir, '*.txt'))):
        ch = os.path.splitext(os.path.basename(f))[0]
        sp, tp = src_paras(book, ch), tr_paras(book, ch)
        for i in range(min(len(sp), len(tp))):
            items.append((book, ch, i + 1, sp[i], tp[i]))
    return items


def yeshu_docx_items():
    """業疏：out 的段落順序與分卷不同，改讀已正確配對的 docx。"""
    from docx import Document
    import glob as _glob
    items = []
    for f in sorted(_glob.glob(os.path.join(B, '白話', '業疏_卷*_白話對照本.docx'))):
        vol = os.path.splitext(os.path.basename(f))[0].split('_')[1]
        ps = [p.text.strip() for p in Document(f).paragraphs]
        i = 0
        while i < len(ps) - 1:
            t = ps[i]
            if t.startswith('【') and len(t) > 4:
                nxt = ps[i + 1]
                if nxt and not nxt.startswith('【'):
                    items.append(('03_業疏', vol, i + 1, t, nxt))
                    i += 2
                    continue
            i += 1
    return items



def yeshu_items():
    items = []
    sd = os.path.join(B, 'TXT_分卷_標點', '03_業疏')
    for f in sorted(glob.glob(os.path.join(sd, '*.txt'))):
        ch = os.path.splitext(os.path.basename(f))[0]
        src = [x.strip() for x in io.open(f, encoding='utf-8').read().split('\n') if x.strip()]
        tp = os.path.join(B, 'AI語譯', 'out', '03_業疏', ch + '.txt')
        if not os.path.exists(tp):
            continue
        tr = [x for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
        for i in range(min(len(src), len(tr))):
            items.append(('03_業疏', ch, i + 1, src[i], tr[i]))
    return items

def main():
    size = 325000
    if '--size' in sys.argv:
        size = int(sys.argv[sys.argv.index('--size') + 1])
    os.makedirs(OUT, exist_ok=True)
    for f in glob.glob(os.path.join(OUT, '*.txt')):
        os.remove(f)

    groups = [('鈔記', maoji_items()),
              ('戒疏', book_items('02_戒疏', '02_戒疏')),
              ('業疏', yeshu_items()),  # 業疏已重譯，1:1
              ('尼鈔', book_items('04_比丘尼鈔', '04_比丘尼鈔')),
              ('義鈔', book_items('05_拾毗尼義鈔', '05_拾毗尼義鈔'))]

    # 先全部展開，再依大小切檔，最後配全域編號 NN-NNNN
    flat = []
    for gname, items in groups:
        for book, ch, i, orig, trans in items:
            flat.append((gname, book, ch, i, orig, trans))

    # 只送「未審過或譯文改過」的段
    import hashlib, json
    state_fp = os.path.join(B, 'AI語譯', '_work', 'review_state.json')
    state = json.load(io.open(state_fp, encoding='utf-8')) if os.path.exists(state_fp) else {}
    force = '--all' in sys.argv

    def h(s):
        return hashlib.md5((s or '').strip().encode('utf-8')).hexdigest()[:12]

    sent = {}
    if not force and state:
        keep = []
        for x in flat:
            gname, book, ch, i, orig, trans = x
            sid = '%s/%s#%s' % (book, ch, i)
            if state.get(sid) == h(trans):
                continue
            keep.append(x)
            sent[sid] = h(trans)
        print('狀態檔已審 %d，本次送出 %d（原 %d）' % (len(state), len(keep), len(flat)))
        flat = keep
    else:
        for gname, book, ch, i, orig, trans in flat:
            sent['%s/%s#%s' % (book, ch, i)] = h(trans)

    json.dump(sent, io.open(os.path.join(B, 'AI語譯', '_work', 'review_sent.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)

    files = []
    for gname, items in groups:
        curf, cursz = [], 0
        for book, ch, i, orig, trans in items:
            est = len('【00-0000】%s/%s#%d\n【原文】%s\n【譯文】%s\n\n' % (book, ch, i, orig, trans))
            if cursz + est > size and curf:
                files.append(curf)
                curf, cursz = [], 0
            curf.append((gname, book, ch, i, orig, trans))
            cursz += est
        if curf:
            files.append(curf)

    rows = []
    for n, f in enumerate(files, 1):
        head = '# 校閱材料　第%02d檔（%s）\n' % (n, f[0][0])
        head += '# 本檔編號一律為 %02d-NNNN，回報時整串照抄，不可自行重編。\n\n' % n
        out = [head]
        csz = 0
        for k, (gname, book, ch, i, orig, trans) in enumerate(f, 1):
            blk = '【%02d-%04d】%s/%s#%d\n【原文】%s\n【譯文】%s\n\n' % (n, k, book, ch, i, orig, trans)
            out.append(blk)
            csz += len(blk.encode('utf-8'))
        name = '校閱_%02d.txt' % n
        io.open(os.path.join(OUT, name), 'w', encoding='utf-8').write(''.join(out))
        rows.append((name, f[0][0], len(f), csz))

    io.open(os.path.join(OUT, '..', 'index.tsv'), 'w', encoding='utf-8').write(
        'file\tgroup\tsegs\tbytes\n' + '\n'.join('\t'.join(map(str, r)) for r in rows) + '\n')
    print('files', len(rows), 'segs', sum(r[2] for r in rows))
    for r in rows[:3]:
        print(r)


if __name__ == '__main__':
    main()
