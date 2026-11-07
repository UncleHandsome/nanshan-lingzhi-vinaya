# -*- coding: utf-8 -*-
"""用「純漢字 + 異體字統一 + 三錨點 + 譯文反查 + 跨 chunk」定位校閱報告。

用法：
    python _src/locate_report.py t3

讀  AI語譯/_work/review/report_<name>.tsv
寫  AI語譯/_work/review/located_<name>.tsv
"""
import os, io, re, sys, csv, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RV = os.path.join(B, 'AI語譯', '_work', 'review')
BOOKS = [('01_行事鈔', '01_行事鈔'), ('02_戒疏', '02_戒疏'), ('03_業疏', '03_業疏'),
         ('資持記', '資持記_細分'), ('04_比丘尼鈔', '04_比丘尼鈔'), ('05_拾毗尼義鈔', '05_拾毗尼義鈔')]

VAR = str.maketrans({'祗': '祇', '缽': '鉢', '尚': '上', '並': '并', '裡': '裏',
                     '褶': '襵', '倶': '俱', '爲': '為', '阇': '闍', '臺': '台',
                     '說': '説', '眾': '衆', '卽': '即', '旣': '既', '敎': '教'})


def clean(s):
    return re.sub(r'[^\u4e00-\u9fa5]', '', s or '').translate(VAR)


def anchors(s, n=8):
    s = clean(s)
    if not s:
        return []
    if len(s) <= n:
        return [s]
    return [s[:n], s[len(s) // 2:len(s) // 2 + n], s[-n:]]


def load_book(book, srcdir):
    """回傳 [(chunk, idx, clean_src, clean_tr), ...]"""
    rows = []
    outd = os.path.join(B, 'AI語譯', 'out', book)
    srcd = os.path.join(B, 'TXT_分卷', srcdir)
    for f in sorted(glob.glob(os.path.join(srcd, '*.txt'))):
        chunk = os.path.splitext(os.path.basename(f))[0]
        src = [x.strip() for x in io.open(f, encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tp = os.path.join(outd, chunk + '.txt')
        if not os.path.exists(tp):
            continue
        tr = [x for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
        for i, s in enumerate(src):
            t = tr[i] if i < len(tr) else ''
            rows.append((chunk, i, clean(s), clean(t)))
    return rows


def score(an_s, an_t, row):
    _, _, cs, ct = row
    sc = 0
    for a in an_s:
        if a and a in cs:
            sc += 2
    for a in an_t:
        if a and a in ct:
            sc += 2
    # 譯文是最可靠的：直接以長段比對
    return sc


def locate(it, books, idx_cache):
    an_s = anchors(it['orig'])
    an_t = anchors(it['tr'])
    order = []
    # 1) 指定 chunk
    if it['chunk'] and it['chunk'] != '?':
        order.append((it['book'], it['chunk']))
    # 2) 同書全部
    for b, _ in BOOKS:
        if b == it['book']:
            order.append((b, None))
    # 3) 其他書
    for b, _ in BOOKS:
        order.append((b, None))

    seen = set()
    for b, only_chunk in order:
        key = (b, only_chunk)
        if key in seen:
            continue
        seen.add(key)
        rows = idx_cache[b]
        best = None
        for row in rows:
            if only_chunk and row[0] != only_chunk:
                continue
            sc = score(an_s, an_t, row)
            if best is None or sc > best[0]:
                best = (sc, row)
            if sc >= 6:
                break
        if best and best[0] >= 4:
            return b, best[1][0], best[1][1] + 1, best[0]
    return None, None, None, 0

def main():
    name = sys.argv[1]
    rows = list(csv.DictReader(io.open(os.path.join(RV, 'report_%s.tsv' % name), encoding='utf-8'), delimiter='\t'))
    idx = {}
    for b, srcdir in BOOKS:
        idx[b] = load_book(b, srcdir)
        print('loaded', b, len(idx[b]))

    out = []
    hit = 0
    for it in rows:
        lb, lch, ls, sc = locate(it, BOOKS, idx)
        ok = lb is not None
        hit += ok
        out.append(dict(it, loc_book=lb or '', loc_chunk=lch or '',
                        loc_seg=ls or '', score=sc, located='Y' if ok else 'N'))

    fp = os.path.join(RV, 'located_%s.tsv' % name)
    with io.open(fp, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, delimiter='\t', fieldnames=list(out[0].keys()))
        w.writeheader()
        for r in out:
            w.writerow(r)

    # 另存一份可直接給 apply_review_fixes 用的報告
    rp = os.path.join(RV, 'report_%s_located.tsv' % name)
    with io.open(rp, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, delimiter='\t', fieldnames=[
            'book', 'chunk', 'seg', 'level', 'cls', 'status', 'problem', 'suggestion',
            'orig', 'tr', 'current'], extrasaction='ignore')
        w.writeheader()
        for r in out:
            if r['located'] != 'Y':
                continue
            w.writerow(dict(r, book=r['loc_book'], chunk=r['loc_chunk'],
                            seg=r['loc_seg'], status='ok', current=''))
    print('located %d / %d' % (hit, len(out)))
    print('→', fp)
    print('→', rp)


if __name__ == '__main__':
    main()
