# -*- coding: utf-8 -*-
"""找出「已歸檔但譯文疑似未落實」的校對意見，輸出待複核清單。

判定：把 fix 正規化（去標籤、引號、標點）後取前 8 字，若未出現在對應段落，
且 fix 長度 >= 10，即列為待複核。
"""
import os, io, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
DONE = os.path.join(B, 'AI語譯', 'review_done')
OUT = os.path.join(B, 'AI語譯', '_work', 'recheck')
LEAD = re.compile(r'^【[^】]{1,6}】')


def norm(s):
    s = LEAD.sub('', s)
    s = re.sub(r'[「」『』（）()：:，,。、；;！!？?\s]', '', s)
    return s


def paras(p):
    return [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8').read()) if x.strip()]


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        os.remove(os.path.join(OUT, f))
    bucket = {}
    for f in sorted(os.listdir(DONE)):
        if not f.endswith('.json'):
            continue
        book, key = f[:-5].split('__', 1)
        p = os.path.join(B, 'AI語譯', 'out', book, key + '.txt')
        if not os.path.exists(p):
            continue
        ps = paras(p)
        items = json.load(io.open(os.path.join(DONE, f), encoding='utf-8'))
        miss = []
        for it in items:
            fix = norm(it.get('fix') or '')
            if len(fix) < 10:
                continue
            seg = int(it.get('seg', 0))
            if not (1 <= seg <= len(ps)):
                continue
            body = norm(ps[seg - 1])
            if fix[:8] not in body:
                miss.append(dict(seg=seg, kind=it.get('kind'), issue=(it.get('issue') or '')[:200],
                                 quote=(it.get('quote') or '')[:60], fix=(it.get('fix') or '')[:200],
                                 cur=ps[seg - 1][:200]))
        if miss:
            bucket[f[:-5]] = miss
    for k, v in bucket.items():
        io.open(os.path.join(OUT, k + '.json'), 'w', encoding='utf-8').write(json.dumps(v, ensure_ascii=False, indent=1))
    total = sum(len(v) for v in bucket.values())
    print('chunks', len(bucket), 'items', total)
    for k, v in sorted(bucket.items(), key=lambda x: -len(x[1]))[:10]:
        print('  ', k, len(v))


if __name__ == '__main__':
    main()
