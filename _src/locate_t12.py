# -*- coding: utf-8 -*-
"""定位 t1/t2 報告（無 chunk 名稱）並輸出可套用的 report TSV。"""
import io, os, re, glob, csv, sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RV = os.path.join(B, 'AI語譯', '_work', 'review')
VAR = str.maketrans({'祗': '祇', '缽': '鉢', '並': '并', '裡': '裏', '爲': '為'})
BOOKS = [('01_行事鈔', '01_行事鈔'), ('02_戒疏', '02_戒疏'), ('03_業疏', '03_業疏'),
         ('資持記', '資持記_細分'), ('04_比丘尼鈔', '04_比丘尼鈔'), ('05_拾毗尼義鈔', '05_拾毗尼義鈔')]


def clean(s):
    return re.sub(r'[^\u4e00-\u9fa5]', '', s or '').translate(VAR)


def anc(s, n=8):
    s = clean(s)
    if not s:
        return []
    return [s[:n], s[len(s) // 2:len(s) // 2 + n], s[-n:]] if len(s) > n else [s]


def build_index():
    idx = {}
    for b, sd in BOOKS:
        rows = []
        for f in glob.glob(os.path.join(B, 'TXT_分卷', sd, '*.txt')):
            ch = os.path.splitext(os.path.basename(f))[0]
            src = [x.strip() for x in io.open(f, encoding='utf-8').read().split('\n')[5:] if x.strip()]
            tp = os.path.join(B, 'AI語譯', 'out', b, ch + '.txt')
            if not os.path.exists(tp):
                continue
            tr = [x for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
            for i, x in enumerate(src):
                rows.append((ch, i + 1, clean(x), clean(tr[i]) if i < len(tr) else '', tr[i] if i < len(tr) else ''))
        idx[b] = rows
    return idx


def parse(p):
    out, cur = [], None
    for line in io.open(p, encoding='utf-8'):
        line = line.rstrip('\n')
        m = re.match(r'^#{2,4}\s*.*?段\s*(\d+)\s*[｜|]\s*(P[012])\s*[｜|]\s*(.*)$', line.strip())
        if m:
            if cur:
                out.append(cur)
            cur = {'seg': int(m.group(1)), 'level': m.group(2), 'cls': m.group(3).strip(),
                   'orig': '', 'tr': '', 'problem': '', 'sug': ''}
            continue
        if cur:
            f = re.match(r'^[-*]\s*\**\s*(原文|譯文|原譯|問題|建議)\s*\**\s*[：:]\s*(.*)$', line.strip())
            if f:
                k = {'原譯': '譯文'}.get(f.group(1), f.group(1))
                key = {'原文': 'orig', '譯文': 'tr', '問題': 'problem', '建議': 'sug'}[k]
                cur[key] = (cur[key] + ' ' + f.group(2).strip()).strip()
    if cur:
        out.append(cur)
    return out


def locate(it, idx):
    A, T = anc(it['orig']), anc(it['tr'])
    best = None
    for b, rows in idx.items():
        for ch, seg, cs, ct, raw in rows:
            sc = sum(2 for a in A if a and a in cs) + sum(2 for a in T if a and a in ct)
            if best is None or sc > best[0]:
                best = (sc, b, ch, seg, raw)
            if sc >= 10:
                break
        if best and best[0] >= 10:
            break
    return best


def main():
    idx = build_index()
    for name, minseg in (('t1', 552), ('t2', 0)):
        items = [x for x in parse(os.path.join(B, '校閱批次', name + '.txt')) if x['seg'] >= minseg]
        rows = []
        for it in items:
            best = locate(it, idx)
            if not best or best[0] < 6:
                continue
            rows.append(dict(book=best[1], chunk=best[2], seg=best[3], level=it['level'], cls=it['cls'],
                             status='ok', problem=it['problem'], suggestion=it['sug'],
                             orig=it['orig'], tr=it['tr'], current=best[4]))
        fp = os.path.join(RV, 'report_%s_located.tsv' % name)
        os.makedirs(RV, exist_ok=True)
        with io.open(fp, 'w', encoding='utf-8', newline='') as fh:
            w = csv.DictWriter(fh, delimiter='\t', fieldnames=['book', 'chunk', 'seg', 'level', 'cls',
                                                               'status', 'problem', 'suggestion',
                                                               'orig', 'tr', 'current'])
            w.writeheader()
            for r in rows:
                w.writerow(r)
        print(name, 'items', len(items), 'located', len(rows), '->', fp)


if __name__ == '__main__':
    main()
