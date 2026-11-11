# -*- coding: utf-8 -*-
"""驗證 10K_第5輪 九檔：格式、段數、原文與譯文來源、有無 append 段。"""
import io, os, re, json, difflib

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D4 = os.path.join(B, '測試_80K對照', '10K_第4輪')
D5 = os.path.join(B, '測試_80K對照', '10K_第5輪')
OUT = os.path.join(B, 'AI語譯', 'out')
LBL = re.compile(r'^【(001-\d{4})】(\S+?)#(\d+)$')


def read(p):
    return io.open(p, encoding='utf-8', newline='').read()


def parse(text):
    lines = text.split('\r\n')
    i0 = next(i for i, l in enumerate(lines) if l.strip() == '# 材料開始')
    segs, cur = [], None
    for l in lines[i0 + 1:]:
        m = LBL.match(l.strip())
        if m:
            cur = dict(label=l.strip(), sid=m.group(1), src=m.group(2), seg=int(m.group(3)),
                       orig=None, trans=None, raw=None)
            segs.append(cur)
            continue
        if cur is None:
            continue
        if l.startswith('【原文】'):
            cur['orig'] = l[4:]
        elif l.startswith('【譯文】'):
            cur['trans'] = l[4:]
    return segs


ok = True
total = 0
for fn in sorted(f for f in os.listdir(D4) if f.endswith('.txt')):
    t4, t5 = read(os.path.join(D4, fn)), read(os.path.join(D5, fn))
    s4, s5 = parse(t4), parse(t5)
    # 1. 段數、段號、原文一致
    assert len(s4) == len(s5), (fn, len(s4), len(s5))
    for a, b in zip(s4, s5):
        if a['label'] != b['label'] or a['orig'] != b['orig']:
            ok = False
            print('!! label/orig mismatch', fn, a['label'], b['label'])
        book, chunk = b['src'].split('/')
        raw = read(os.path.join(OUT, book, chunk + '.txt'))
        seg = raw.split('\r\n\r\n')
        while seg and seg[-1].strip() == '':
            seg.pop()
        if seg[b['seg'] - 1].strip() != b['trans']:
            ok = False
            print('!! trans != out', fn, b['label'])
    # 2. 無 append 區塊
    for bad in ('# 你剛才的回報', '# 追問', '還有嗎？', '確定沒有了嗎'):
        if bad in t5:
            ok = False
            print('!! contains', bad, fn)
    # 3. 結構：只有一個 --- 分隔、# 標題僅兩處
    heads = [l for l in t5.split('\r\n') if l.startswith('# ')]
    assert heads == ['# 校閱材料\u3000第001檔（第5輪）', '# 材料開始'], (fn, heads)
    assert t5.count('\r\n---\r\n') == 1, (fn, t5.count('\r\n---\r\n'))
    assert t5.endswith('\r\n') and not t5.endswith('\r\n\r\n')
    assert '\n' not in t5.replace('\r\n', ''), 'bare LF in ' + fn
    total += len(s5)
    print('%s  段 %d  %s～%s  bytes %d' % (fn, len(s5), s5[0]['sid'], s5[-1]['sid'],
                                          len(t5.encode('utf-8'))))
print('ALL OK' if ok else 'FAILED', 'total segs', total)
