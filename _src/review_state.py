# -*- coding: utf-8 -*-
"""校閱狀態：記錄每段「已審過的譯文 hash」，讓下一輪只出未審或改過的段。

用法：
    python _src/review_state.py --stats
    python _src/review_state.py --mark-sent      # 把上次送出的段標為已審
    python _src/review_state.py --seed 檔案.tsv  # 從既有報告補登（book/chunk/seg 欄）

狀態檔：AI語譯/_work/review_state.json
送出紀錄：AI語譯/_work/review_sent.json（由 review_pack.py 產生）
"""
import os, io, re, sys, json, hashlib, csv

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
STATE = os.path.join(B, 'AI語譯', '_work', 'review_state.json')
SENT = os.path.join(B, 'AI語譯', '_work', 'review_sent.json')


def seg_id(book, ch, seg):
    return '%s/%s#%s' % (book, ch, seg)


def text_hash(s):
    return hashlib.md5((s or '').strip().encode('utf-8')).hexdigest()[:12]


def load(p, default):
    if os.path.exists(p):
        return json.load(io.open(p, encoding='utf-8'))
    return default


def save(p, d):
    json.dump(d, io.open(p, 'w', encoding='utf-8'), ensure_ascii=False)


def out_para(book, ch, seg):
    p = os.path.join(B, 'AI語譯', 'out', book, ch + '.txt')
    if not os.path.exists(p):
        return None
    ps = [x for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8').read()) if x.strip()]
    i = int(seg) - 1
    return ps[i] if 0 <= i < len(ps) else None


def main():
    st = load(STATE, {})
    args = sys.argv[1:]
    if '--stats' in args or not args:
        print('已審段數', len(st))
        return
    if '--mark-sent' in args:
        sent = load(SENT, {})
        for k, h in sent.items():
            st[k] = h
        save(STATE, st)
        print('已標記', len(sent), '段；狀態共', len(st))
        return
    if '--seed' in args:
        fp = args[args.index('--seed') + 1]
        n = 0
        for r in csv.DictReader(io.open(fp, encoding='utf-8'), delimiter='\t'):
            b, ch, seg = r.get('book'), r.get('chunk'), r.get('seg')
            if not (b and ch and seg):
                continue
            t = out_para(b, ch, seg)
            if t is None:
                continue
            st[seg_id(b, ch, seg)] = text_hash(t)
            n += 1
        save(STATE, st)
        print('補登', n, '段；狀態共', len(st))
        return
    print('用法：--stats / --mark-sent / --seed <tsv>')


if __name__ == '__main__':
    main()
