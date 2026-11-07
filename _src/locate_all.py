# -*- coding: utf-8 -*-
"""重新定位校閱報告（t1–t4）：用原文 10-gram 投票，跨全部六書。

修正兩個 bug：
  1. current 取譯文（out），不是原文。
  2. 業疏原文用 TXT_分卷_標點/03_業疏（路徑含書名層）。

輸出：AI語譯/_work/review/located_all2.tsv
"""
import os, io, re, glob, csv, collections

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RV = os.path.join(B, 'AI語譯', '_work', 'review')

BOOKS = [
    ('01_行事鈔', os.path.join(B, 'TXT_分卷', '01_行事鈔')),
    ('02_戒疏', os.path.join(B, 'TXT_分卷', '02_戒疏')),
    ('03_業疏', os.path.join(B, 'TXT_分卷_標點', '03_業疏')),
    ('資持記', os.path.join(B, 'TXT_分卷', '資持記_細分')),
    ('04_比丘尼鈔', os.path.join(B, 'TXT_分卷', '04_比丘尼鈔')),
    ('05_拾毗尼義鈔', os.path.join(B, 'TXT_分卷', '05_拾毗尼義鈔')),
]


def clean(s):
    return re.sub(r'[^\u4e00-\u9fa5]', '', s or '')


def load_src(book, d):
    out = []
    for f in sorted(glob.glob(os.path.join(d, '*.txt'))):
        ch = os.path.splitext(os.path.basename(f))[0]
        raw = io.open(f, encoding='utf-8').read()
        if book == '03_業疏':                 # 分卷_標點：空行分段，無檔頭
            ps = [x.strip() for x in re.split(r'\r?\n\r?\n', raw) if x.strip()]
        else:
            ps = [x.strip() for x in raw.split('\n')[5:] if x.strip()]
        out.append((ch, ps))
    return out


def load_tr(book, ch):
    p = os.path.join(B, 'AI語譯', 'out', book, ch + '.txt')
    if not os.path.exists(p):
        return []
    return [x for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8').read()) if x.strip()]


def parse_report(name):
    t = io.open(os.path.join(B, '校閱批次', name + '.txt'), encoding='utf-8').read()
    items = []
    for m in re.finditer(r'###\s*段(\d+)\s*[｜|]\s*(P[012])\s*[｜|]\s*([^\n]*)\n(.*?)(?=\n###\s*段|\Z)', t, re.S):
        seg, lvl, cls, body = int(m.group(1)), m.group(2), m.group(3).strip(), m.group(4)

        def f(k):
            mm = re.search(r'[-*]\s*\**\s*' + k + r'\**\s*[：:]\s*(.*)', body)
            return mm.group(1).strip() if mm else ''
        orig, tr = f('原文'), f('譯文')
        if not orig:
            continue
        items.append(dict(src=name, seg=seg, level=lvl, cls=cls, orig=orig, tr=tr,
                          problem=f('問題'), suggestion=f('建議')))
    return items


def main():
    paras, idx = [], collections.defaultdict(set)
    for book, d in BOOKS:
        for ch, ps in load_src(book, d):
            trs = load_tr(book, ch)
            for i, p in enumerate(ps):
                pid = len(paras)
                tr = trs[i] if i < len(trs) else ''
                paras.append(dict(book=book, chunk=ch, seg=i + 1, src=p, tr=tr))
                c = clean(p)
                for k in range(0, max(0, len(c) - 9), 3):
                    idx[c[k:k + 10]].add(pid)
    print('paras', len(paras), 'grams', len(idx))

    items = []
    for n in ('t1', 't2', 't3', 't4'):
        items += parse_report(n)
    # 去重（同原文＋同問題）
    seen = set()
    uniq = []
    for it in items:
        k = (clean(it['orig'])[:40], clean(it['problem'])[:40])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(it)
    print('items', len(items), 'unique', len(uniq))

    rows = []
    for it in uniq:
        c = clean(it['orig'])
        grams = [c[k:k + 10] for k in range(0, max(0, len(c) - 9), 4)][:30]
        votes = collections.Counter()
        for g in grams:
            for pid in idx.get(g, ()):
                votes[pid] += 1
        if votes:
            pid, v = votes.most_common(1)[0]
            p = paras[pid]
            rows.append(dict(src=it['src'], votes=v, book=p['book'], chunk=p['chunk'], seg=p['seg'],
                             level=it['level'], cls=it['cls'], problem=it['problem'],
                             suggestion=it['suggestion'], orig=it['orig'], tr=it['tr'], current=p['tr']))
        else:
            rows.append(dict(src=it['src'], votes=0, book='', chunk='', seg='', level=it['level'],
                             cls=it['cls'], problem=it['problem'], suggestion=it['suggestion'],
                             orig=it['orig'], tr=it['tr'], current=''))

    fp = os.path.join(RV, 'located_all2.tsv')
    with io.open(fp, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, delimiter='\t', fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)

    strong = [r for r in rows if r['votes'] >= 3]
    print('located', sum(1 for r in rows if r['votes']), 'strong', len(strong), 'none',
          sum(1 for r in rows if r['votes'] == 0))
    print('by book (strong):', collections.Counter(r['book'] for r in strong).most_common())
    print('→', fp)


if __name__ == '__main__':
    main()
