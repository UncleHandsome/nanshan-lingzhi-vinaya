# -*- coding: utf-8 -*-
"""把校閱報告（### 段… 格式）解析成 TSV，並對回 AI語譯/out 的段落。

用法：
    python _src/parse_review_report.py 校閱批次/1.txt
輸出：
    AI語譯/_work/review/report_<name>.tsv
欄位：chunk seg level cls status problem suggestion current
status：ok（原文可在現行譯文對應段落找到）、stale（找不到）、nofile
"""
import os, io, re, sys, csv

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BOOKS = ['01_行事鈔', '02_戒疏', '03_業疏', '資持記', '04_比丘尼鈔', '05_拾毗尼義鈔']
SRCDIR = {'01_行事鈔': '01_行事鈔', '02_戒疏': '02_戒疏', '03_業疏': '03_業疏',
          '資持記': '資持記_細分', '04_比丘尼鈔': '04_比丘尼鈔', '05_拾毗尼義鈔': '05_拾毗尼義鈔'}
HEAD = re.compile(r'^#{2,4}\s*(.*?)\s*段\s*(\d{1,4})\s*[｜|]\s*(P[012])\s*[｜|]\s*(.*)$')
CHUNK = re.compile(r'((?:[0-9]{2}[a-z]?)_[^\s/｜|`（(]+)')
FIELD = re.compile(r'^[-*]\s*\**\s*(原文|譯文|原譯|問題|依據|自證|建議|信心)\s*\**\s*[：:]\s*(.*)$')


def parse(path):
    items, cur = [], None
    last_chunk, last_book = '', None
    for line in io.open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        m = HEAD.match(line.strip())
        if not m and line.lstrip().startswith('#'):
            cm = CHUNK.search(line)
            if cm:
                last_chunk = cm.group(1)
                pre = line.strip().lstrip('#').strip()
                last_book = pre.split('/')[0] if '/' in pre and pre.split('/')[0] in BOOKS else None
        if m:
            if cur:
                items.append(cur)
            raw = m.group(1).strip().rstrip('/')
            book = raw.split('/')[0] if '/' in raw else None
            cm = CHUNK.search(raw)
            chunk = cm.group(1) if cm else ''
            if book not in BOOKS:
                book = None
            if not chunk:
                chunk = last_chunk
                book = book or last_book
            if not chunk:
                chunk = '?'
            if chunk != '?':
                last_chunk, last_book = chunk, book
            cur = dict(book=book, chunk=chunk, seg=int(m.group(2)), level=m.group(3),
                       cls=m.group(4).strip(), orig='', tr='', problem='', evid='',
                       suggestion='', conf='')
            continue
        if cur:
            f = FIELD.match(line.strip())
            if f:
                k = f.group(1)
                k = {'原譯': '譯文', '自證': '依據'}.get(k, k)
                v = f.group(2).strip()
                key = {'原文': 'orig', '譯文': 'tr', '問題': 'problem', '依據': 'evid',
                       '建議': 'suggestion', '信心': 'conf'}[k]
                cur[key] = (cur[key] + ' ' + v).strip() if cur[key] else v
    if cur:
        items.append(cur)
    return items


def load_out(book, chunk):
    p = os.path.join(B, 'AI語譯', 'out', book, chunk + '.txt')
    if not os.path.exists(p):
        return None, []
    txt = io.open(p, encoding='utf-8').read()
    return p, [x for x in re.split(r'\r?\n\r?\n', txt) if x.strip()]


def load_src(book, chunk):
    p = os.path.join(B, 'TXT_分卷', SRCDIR.get(book, book), chunk + '.txt')
    if not os.path.exists(p):
        return []
    return [x.strip() for x in io.open(p, encoding='utf-8').read().split('\n')[5:] if x.strip()]


def norm(s):
    s = re.sub(r'【[^】]{1,6}】', '', s)
    return re.sub(r'[\s，。、；：？！「」『』（）()〔〕\[\]〈〉《》`*]', '', s)


def main():
    path = sys.argv[1]
    items = parse(path)
    out = []
    for it in items:
        key = norm(it['orig'])[:14]
        cands = [it['book']] if it['book'] else []
        have = [b for b in BOOKS
                if os.path.exists(os.path.join(B, 'TXT_分卷', SRCDIR[b], it['chunk'] + '.txt'))]
        if it['book'] and it['book'] not in have:
            cands = have          # 標錯書名：改以實際擁有此 chunk 的書為準
        cands = cands + [b for b in have if b not in cands]
        if not cands:
            it['book'] = '01_行事鈔'
            out.append(dict(it, status='nofile', current=''))
            continue
        best = None
        for b in cands:
            src = load_src(b, it['chunk'])
            if not src:
                continue
            k = it['seg'] - 1
            if 0 <= k < len(src) and key and key in norm(src[k]):
                best = (b, k, 'ok')
                break
            for i, x in enumerate(src):
                if key and key in norm(x):
                    best = (b, i, 'shift:%d' % (i + 1))
                    break
            if best:
                break
        if best is None:
            # 退而求其次：從原文中取 12 字窗口，找任何一段含有它
            body = norm(it['orig'])
            wins = [body[i:i + 12] for i in range(0, min(len(body) - 11, 60), 4)]
            for b in cands:
                src = load_src(b, it['chunk'])
                for i, x in enumerate(src):
                    nx = norm(x)
                    if any(w and w in nx for w in wins):
                        best = (b, i, 'win:%d' % (i + 1))
                        break
                if best:
                    break
        if best is None:
            it['book'] = cands[0]
            out.append(dict(it, status='stale', current=''))
            continue
        b, hit, status = best
        it['book'] = b
        ps = load_out(b, it['chunk'])[1]
        cur = ps[hit] if hit < len(ps) else ''
        if not cur:
            status = 'noout'
        out.append(dict(it, status=status, current=cur))

    name = os.path.splitext(os.path.basename(path))[0]
    dst = os.path.join(B, 'AI語譯', '_work', 'review', 'report_%s.tsv' % name)
    with io.open(dst, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, delimiter='\t', fieldnames=['book', 'chunk', 'seg', 'level', 'cls',
                                                           'status', 'problem', 'suggestion',
                                                           'orig', 'tr', 'current'],
                           extrasaction='ignore')
        w.writeheader()
        for r in out:
            w.writerow(r)

    from collections import Counter
    print('items', len(out), Counter(x['level'] for x in out))
    print('status', Counter(x['status'].split(':')[0] for x in out))
    print('→', dst)


if __name__ == '__main__':
    main()
