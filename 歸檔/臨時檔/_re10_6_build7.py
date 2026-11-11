# -*- coding: utf-8 -*-
"""產出 測試_80K對照/10K_第7輪/：沿用第 6 輪六檔的段範圍與原文，譯文換成現行 out。"""
import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D6 = os.path.join(B, '測試_80K對照', '10K_第6輪')
D7 = os.path.join(B, '測試_80K對照', '10K_第7輪')
OUT = os.path.join(B, 'AI語譯', 'out')
PROMPT = os.path.join(B, '校閱批次', '提示詞_白話校閱.md')

LBL = re.compile(r'^【(001-\d{4})】(\S+?)#(\d+)$')
_cache = {}


def read(p, nl=''):
    return io.open(p, encoding='utf-8', newline=nl).read()


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
    prompt = read(PROMPT, '').strip()
    assert '\r\n' in prompt
    os.makedirs(D7, exist_ok=True)
    files = sorted(f for f in os.listdir(D6) if f.endswith('.txt'))
    total = 0
    for fn in files:
        segs = parse_material(read(os.path.join(D6, fn), ''))
        parts, changed = [], []
        for s in segs:
            book, chunk = s['src'].split('/')
            cur = out_segs(book, chunk)[s['seg'] - 1].strip()
            if cur != s['trans']:
                changed.append(s['sid'])
            parts.append(s['line'] + '\r\n【原文】%s\r\n【譯文】%s' % (s['orig'], cur))
        head = ('# 校閱材料\u3000第001檔（第7輪）\r\n\r\n'
                '以下提示詞請連同材料一起貼給 AI：\r\n\r\n'
                + prompt + '\r\n\r\n---\r\n\r\n# 材料開始\r\n\r\n')
        body = head + '\r\n\r\n'.join(parts) + '\r\n'
        io.open(os.path.join(D7, fn), 'w', encoding='utf-8', newline='').write(body)
        total += len(segs)
        print('%-16s %2d 段 %s~%s 譯文更新 %d %s  bytes %d'
              % (fn, len(segs), segs[0]['sid'], segs[-1]['sid'], len(changed),
                 ','.join(changed), len(body.encode('utf-8'))))
    print('files %d  total segs %d' % (len(files), total))


if __name__ == '__main__':
    main()
