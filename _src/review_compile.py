# -*- coding: utf-8 -*-
"""彙整校閱報告：把 _work/review/out/*.md 解析成 findings.tsv 與進度表。

用法：
    python _src/review_compile.py            # 解析全部報告
    python _src/review_compile.py --md 交接/校閱_第1批.md   # 另存合併報告

輸出：
    AI語譯/_work/review/findings.tsv   每條意見一行
    AI語譯/_work/review/progress.tsv   每個 chunk 的狀態
"""
import os, io, re, sys, glob, csv

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
WORK = os.path.join(B, 'AI語譯', '_work', 'review')
OUT = os.path.join(WORK, 'out')

HEAD = re.compile(r'^#{2,4}\s*段\s*(\d{1,4})\s*[｜|]\s*(P[012])\s*[｜|]\s*([A-H])')
FIELD = re.compile(r'^[-*]\s*(原文|原譯|問題|自證|建議|信心)\s*[：:]\s*(.*)$')


def parse_file(path):
    book, chunk = os.path.basename(path)[:-3].split('__', 1)
    chunk = re.sub(r'_\d+-\d+$', '', chunk)
    rows = []
    cur = None
    for line in io.open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        m = HEAD.match(line)
        if m:
            if cur:
                rows.append(cur)
            cur = dict(book=book, chunk=chunk, seg=int(m.group(1)), level=m.group(2),
                       cls=m.group(3), orig='', tr='', problem='', evidence='',
                       suggestion='', conf='')
            continue
        if cur:
            f = FIELD.match(line.strip())
            if f:
                k, v = f.group(1), f.group(2).strip()
                key = {'原文': 'orig', '原譯': 'tr', '問題': 'problem',
                       '自證': 'evidence', '建議': 'suggestion', '信心': 'conf'}[k]
                cur[key] = (cur[key] + ' ' + v).strip() if cur[key] else v
    if cur:
        rows.append(cur)
    return rows


def main():
    args = sys.argv[1:]
    md_path = args[args.index('--md') + 1] if '--md' in args else None

    files = sorted(glob.glob(os.path.join(OUT, '*.md')))
    findings = []
    for f in files:
        findings.extend(parse_file(f))

    order = {'P0': 0, 'P1': 1, 'P2': 2}
    findings.sort(key=lambda r: (order.get(r['level'], 9), r['book'], r['chunk'], r['seg']))

    fp = os.path.join(WORK, 'findings.tsv')
    with io.open(fp, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, delimiter='\t', fieldnames=['book', 'chunk', 'seg', 'level', 'cls',
                                                           'problem', 'orig', 'tr', 'evidence',
                                                           'suggestion', 'conf'])
        w.writeheader()
        for r in findings:
            w.writerow(r)

    done = {}
    for f in files:
        b, c = os.path.basename(f)[:-3].split('__', 1)
        c = re.sub(r'_\d+-\d+$', '', c)
        done[(b, c)] = done.get((b, c), 0) + 1

    pp = os.path.join(WORK, 'progress.tsv')
    total = 0
    with io.open(pp, 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh, delimiter='\t')
        w.writerow(['book', 'chunk', 'segs_done', 'findings'])
        for (b, c), n in sorted(done.items()):
            w.writerow([b, c, n, n])
            total += n

    cnt = {}
    for r in findings:
        cnt[r['level']] = cnt.get(r['level'], 0) + 1
    print('報告 %d 份、chunk %d 個、意見 %d 條（P0 %d、P1 %d、P2 %d）'
          % (len(files), len(done), len(findings), cnt.get('P0', 0), cnt.get('P1', 0), cnt.get('P2', 0)))
    print('→', fp)
    print('→', pp)

    if md_path:
        lines = ['# 校閱合併報告', '', '來源：`AI語譯/_work/review/out/*.md`', '',
                 '| 級別 | 數量 |', '|:--|--:|']
        for k in ('P0', 'P1', 'P2'):
            lines.append('| %s | %d |' % (k, cnt.get(k, 0)))
        lines += ['', '---', '']
        for r in findings:
            lines.append('### %s / %s 段%03d ｜ %s ｜ %s' % (r['book'], r['chunk'], r['seg'], r['level'], r['cls']))
            if r['problem']:
                lines.append('- 問題：%s' % r['problem'])
            if r['orig']:
                lines.append('- 原文：%s' % r['orig'])
            if r['tr']:
                lines.append('- 原譯：%s' % r['tr'])
            if r['evidence']:
                lines.append('- 自證：%s' % r['evidence'])
            if r['suggestion']:
                lines.append('- 建議：%s' % r['suggestion'])
            lines.append('')
        io.open(md_path, 'w', encoding='utf-8').write('\n'.join(lines))
        print('→', md_path)


if __name__ == '__main__':
    main()
