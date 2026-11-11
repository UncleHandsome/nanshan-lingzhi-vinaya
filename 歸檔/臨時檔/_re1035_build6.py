# -*- coding: utf-8 -*-
"""產出 測試_80K對照/10K_第6輪/（乾淨版：提示詞＋材料，無 append、無追問）。

只產出「第 4 輪或第 5 輪至少有一條意見」的檔案。
"""
import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D5 = os.path.join(B, '測試_80K對照', '10K_第5輪')
D6 = os.path.join(B, '測試_80K對照', '10K_第6輪')
OUT = os.path.join(B, 'AI語譯', 'out')
PROMPT = os.path.join(B, '校閱批次', '提示詞_白話校閱.md')

LBL = re.compile(r'^【(001-\d{4})】(\S+?)#(\d+)$')
_cache = {}


def read(p, nl=''):
    return io.open(p, encoding='utf-8', newline=nl).read()


def sids_round(fn):
    t = read(os.path.join(B, '測試_80K對照', fn))
    return set(re.findall(r'^###\s*(001-\d{4})｜', t, re.M))


def parse_material(text):
    lines = text.splitlines()
    i0 = next(i for i, l in enumerate(lines) if l.strip() == '# 材料開始')
    segs, cur = [], None
    for l in lines[i0 + 1:]:
        m = LBL.match(l.strip())
        if m:
            cur = dict(line=l.strip(), sid=m.group(1), src=m.group(2), seg=int(m.group(3)),
                       orig=None, trans=None)
            segs.append(cur)
            continue
        if cur is None:
            continue
        if l.startswith('【原文】'):
            cur['orig'] = l[4:]
        elif l.startswith('【譯文】'):
            cur['trans'] = l[4:]
    return segs


def out_segs(book, chunk):
    key = (book, chunk)
    if key not in _cache:
        raw = read(os.path.join(OUT, book, chunk + '.txt'), '')
        seg = raw.split('\r\n\r\n')
        while seg and seg[-1].strip() == '':
            seg.pop()
        _cache[key] = seg
    return _cache[key]


def main():
    r4, r5 = sids_round('10_4.txt'), sids_round('10_5.txt')
    prompt = read(PROMPT, '').strip()
    assert '\r\n' in prompt
    os.makedirs(D6, exist_ok=True)
    files = sorted(f for f in os.listdir(D5) if f.endswith('.txt'))
    stats, total, kept = [], 0, 0
    for fn in files:
        segs = parse_material(read(os.path.join(D5, fn), ''))
        n4 = len([s for s in segs if s['sid'] in r4])
        n5 = len([s for s in segs if s['sid'] in r5])
        row = dict(file=fn, n=len(segs), first=segs[0]['sid'], last=segs[-1]['sid'],
                   r4=n4, r5=n5)
        if not (n4 or n5):
            row['kept'] = False
            stats.append(row)
            print('%s  排除（%s~%s，%d 段；R4 0、R5 0）'
                  % (fn, segs[0]['sid'], segs[-1]['sid'], len(segs)))
            continue
        row['kept'] = True
        parts, changed = [], 0
        for s in segs:
            book, chunk = s['src'].split('/')
            cur = out_segs(book, chunk)[s['seg'] - 1].strip()
            if cur != s['trans']:
                changed += 1
            parts.append(s['line'] + '\r\n【原文】%s\r\n【譯文】%s' % (s['orig'], cur))
        head = ('# 校閱材料\u3000第001檔（第6輪）\r\n\r\n'
                '以下提示詞請連同材料一起貼給 AI：\r\n\r\n'
                + prompt + '\r\n\r\n---\r\n\r\n# 材料開始\r\n\r\n')
        body = head + '\r\n\r\n'.join(parts) + '\r\n'
        io.open(os.path.join(D6, fn), 'w', encoding='utf-8', newline='').write(body)
        row.update(replaced=changed, bytes=len(body.encode('utf-8')))
        stats.append(row)
        total += len(segs)
        kept += 1
        print('%s  %d 段  %s~%s  R4 %d、R5 %d  譯文更新 %d  bytes %d'
              % (fn, len(segs), segs[0]['sid'], segs[-1]['sid'], n4, n5, changed,
                 len(body.encode('utf-8'))))
    print('kept %d files, total %d segs' % (kept, total))
    json.dump(stats, io.open(os.path.join(B, '歸檔', '臨時檔', '_re1035_r6stats.json'), 'w',
                             encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
