# -*- coding: utf-8 -*-
"""產生「測試材料」：30 段已知有錯（用修正前的舊譯）＋70 段隨機乾淨段，混排。

用途：讓 AI 跑一次，看它能抓到幾段已知錯誤（召回率），以及對乾淨段誤報多少（誤報率）。
答案存在 key.tsv，不要給 AI。
"""
import os, io, re, glob, csv, random, collections

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RV = os.path.join(B, 'AI語譯', '_work', 'review')
OUT = os.path.join(B, '測試材料')
BOOK_DIR = {'01_行事鈔': '01_行事鈔', '02_戒疏': '02_戒疏', '03_業疏': 'TXT_分卷_標點',
            '資持記': '資持記_細分', '04_比丘尼鈔': '04_比丘尼鈔', '05_拾毗尼義鈔': '05_拾毗尼義鈔'}


def paras(book, ch):
    p = os.path.join(B, 'AI語譯', 'out', book, ch + '.txt')
    return [x for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8').read()) if x.strip()]


def source(book, ch):
    if book == '03_業疏':
        p = os.path.join(B, 'TXT_分卷_標點', '03_業疏', ch + '.txt')
        return [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8').read()) if x.strip()]
    p = os.path.join(B, 'TXT_分卷', BOOK_DIR[book], ch + '.txt')
    return [x.strip() for x in io.open(p, encoding='utf-8').read().split('\n')[5:] if x.strip()]


def main():
    os.makedirs(OUT, exist_ok=True)
    # 修正前舊譯（含錯）
    dirty = {}
    for d in glob.glob(os.path.join(RV, 'backup_err2_*')):
        for f in glob.glob(os.path.join(d, '*.txt')):
            ch = os.path.splitext(os.path.basename(f))[0]
            old = [x for x in re.split(r'\r?\n\r?\n', io.open(f, encoding='utf-8').read()) if x.strip()]
            for book in ('01_行事鈔', '02_戒疏', '資持記'):
                if not os.path.exists(os.path.join(B, 'AI語譯', 'out', book, ch + '.txt')):
                    continue
                cur = paras(book, ch)
                if not cur:
                    continue
                for i, t in enumerate(old):
                    if i < len(cur) and t != cur[i]:
                        dirty[(book, ch, i + 1)] = t
                break
    by_book = collections.defaultdict(list)
    for (b, ch, s), t in dirty.items():
        by_book[b].append((b, ch, s, t))
    random.seed(20261108)
    picked = []
    for b, lst in by_book.items():
        random.shuffle(lst)
        picked += lst[:10]
    picked = picked[:30]

    fixed = set((b, ch, s) for b, ch, s, _ in picked)
    clean = []
    for book in ('01_行事鈔', '02_戒疏', '03_業疏', '資持記', '04_比丘尼鈔', '05_拾毗尼義鈔'):
        for f in sorted(glob.glob(os.path.join(B, 'AI語譯', 'out', book, '*.txt'))):
            ch = os.path.splitext(os.path.basename(f))[0]
            ps = paras(book, ch)
            for i in range(len(ps)):
                if (book, ch, i + 1) not in fixed:
                    clean.append((book, ch, i + 1))
    random.shuffle(clean)
    clean = clean[:70]

    rows = []
    for b, ch, s, t in picked:
        rows.append((b, ch, s, 'dirty'))
    for b, ch, s in clean:
        rows.append((b, ch, s, 'clean'))
    random.shuffle(rows)

    lines = ['# 校閱測試材料（100 段，混合）\n# 編號 T-0001 起，回報時連同 書/chunk#段 一起照抄。\n\n']
    key = []
    for n, (b, ch, s, kind) in enumerate(rows, 1):
        src = source(b, ch)
        cur = paras(b, ch)
        tr = dirty.get((b, ch, s), cur[s - 1]) if kind == 'dirty' else cur[s - 1]
        lines.append('【T-%04d】%s/%s#%d\n【原文】%s\n【譯文】%s\n\n' % (n, b, ch, s, src[s - 1], tr))
        key.append((n, b, ch, s, kind))
    io.open(os.path.join(OUT, '測試_100段.txt'), 'w', encoding='utf-8').write(''.join(lines))
    with io.open(os.path.join(OUT, 'key.tsv'), 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh, delimiter='\t')
        w.writerow(['id', 'book', 'chunk', 'seg', 'kind'])
        for r in key:
            w.writerow(r)
    print('rows', len(rows), 'dirty', sum(1 for r in rows if r[3] == 'dirty'),
          'clean', sum(1 for r in rows if r[3] == 'clean'))


if __name__ == '__main__':
    main()
