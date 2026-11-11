# -*- coding: utf-8 -*-
"""解析第 3／5 輪校閱結果，定位到 out 段，dump 現行譯文供判讀。"""
import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, '測試_80K對照')
OUT = os.path.join(B, 'AI語譯', 'out')
WORK = os.path.join(B, '歸檔', '臨時檔')
FILES = [('10_3.txt', '3'), ('10_3_1.txt', '3'), ('10_5.txt', '5')]

HEAD = re.compile(r'^###\s*(001-\d{4})｜(\S+?)｜(P\d)｜(.+?)\s*$')
FIELD = re.compile(r'^-\s*(原文起首|問題|依據|建議|信心)：(.*)$')


def parse(path, rnd):
    items, cur = [], None
    for line in io.open(path, encoding='utf-8').read().splitlines():
        s = line.rstrip()
        m = HEAD.match(s)
        if m:
            cur = dict(round=rnd, sid=m.group(1), loc=m.group(2), pri=m.group(3), kind=m.group(4),
                       src_file=os.path.basename(path), orig_head='', issue='', basis='', sug='',
                       conf='')
            items.append(cur)
            continue
        if cur is None:
            continue
        m = FIELD.match(s)
        if m:
            k = m.group(1)
            v = m.group(2).strip()
            key = {'原文起首': 'orig_head', '問題': 'issue', '依據': 'basis',
                   '建議': 'sug', '信心': 'conf'}[k]
            cur[key] = (cur[key] + ' ' + v).strip() if cur[key] else v
    return items


def load_labels():
    """校閱_80K/校閱_001.txt → {段號: (book, chunk, seg)}"""
    t = io.open(os.path.join(B, '校閱_80K', '校閱_001.txt'), encoding='utf-8').read()
    lines = t.splitlines()
    lab, orig, trans = {}, {}, {}
    cur = None
    for i, l in enumerate(lines):
        m = re.match(r'^【(001-\d{4})】(\S+?)#(\d+)$', l.strip())
        if m:
            book, chunk = m.group(2).split('/')
            cur = m.group(1)
            lab[cur] = (book, chunk, int(m.group(3)))
            continue
        if cur and l.startswith('【原文】'):
            orig[cur] = l[4:]
        elif cur and l.startswith('【譯文】'):
            trans[cur] = l[4:]
    return lab, orig, trans


_cache = {}


def out_segs(book, chunk):
    k = (book, chunk)
    if k not in _cache:
        raw = io.open(os.path.join(OUT, book, chunk + '.txt'), encoding='utf-8', newline='').read()
        seg = raw.split('\r\n\r\n')
        while seg and seg[-1].strip() == '':
            seg.pop()
        _cache[k] = seg
    return _cache[k]


def main():
    lab, orig80, trans80 = load_labels()
    all_items = []
    for fn, rnd in FILES:
        p = os.path.join(SRC, fn)
        if not os.path.exists(p):
            continue
        for it in parse(p, rnd):
            all_items.append(it)

    rows = []
    for it in all_items:
        sid = it['sid']
        if sid not in lab:
            it['error'] = 'unmapped'
            rows.append(it)
            continue
        book, chunk, seg = lab[sid]
        it['book'], it['chunk'], it['seg'] = book, chunk, seg
        try:
            cur_txt = out_segs(book, chunk)[seg - 1].strip()
        except IndexError:
            cur_txt = ''
        it['out_cur'] = cur_txt
        it['out80'] = trans80.get(sid, '')
        it['orig'] = orig80.get(sid, '')
        rows.append(it)

    json.dump(rows, io.open(os.path.join(WORK, '_re1035_items.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    print('total items', len(rows))
    for i, it in enumerate(rows, 1):
        print('\n' + '=' * 100)
        print('#%d [R%s] %s %s %s %s' % (i, it['round'], it['sid'], it['loc'], it['pri'], it['kind']))
        print('  head :', it['orig_head'])
        print('  issue:', it['issue'])
        print('  sug  :', it['sug'])
        print('  conf :', it['conf'])
        print('  --ORIG80--')
        print('  ' + it.get('orig', '')[:400])
        print('  --OUT_CUR (seg %s)--' % it.get('seg'))
        print('  ' + it.get('out_cur', '')[:900])


if __name__ == '__main__':
    main()
