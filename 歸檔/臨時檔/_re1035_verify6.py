# -*- coding: utf-8 -*-
"""驗證第 6 輪材料：提示詞全文、段號與第 5 輪一致、原文不變、譯文＝現行 out。"""
import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D5 = os.path.join(B, '測試_80K對照', '10K_第5輪')
D6 = os.path.join(B, '測試_80K對照', '10K_第6輪')
OUT = os.path.join(B, 'AI語譯', 'out')

LBL = re.compile(r'^【(001-\d{4})】(\S+?)#(\d+)$')


def parse(t):
    lines = t.splitlines()
    i0 = [i for i, l in enumerate(lines) if l.strip() == '# 材料開始'][0]
    segs, cur = [], None
    for l in lines[i0 + 1:]:
        m = LBL.match(l.strip())
        if m:
            cur = dict(sid=m.group(1), src=m.group(2), seg=int(m.group(3)), o=None, t=None)
            segs.append(cur)
            continue
        if cur is None:
            continue
        if l.startswith('【原文】'):
            cur['o'] = l[4:]
        elif l.startswith('【譯文】'):
            cur['t'] = l[4:]
    return segs


def out_arr(book, chunk):
    raw = io.open(os.path.join(OUT, book, chunk + '.txt'), encoding='utf-8', newline='').read()
    arr = raw.split('\r\n\r\n')
    while arr and arr[-1].strip() == '':
        arr.pop()
    return arr


def main():
    prompt = io.open(os.path.join(B, '校閱批次', '提示詞_白話校閱.md'), encoding='utf-8',
                     newline='').read().strip()
    bad = 0
    tot = 0
    for fn in sorted(os.listdir(D6)):
        t6 = io.open(os.path.join(D6, fn), encoding='utf-8', newline='').read()
        t5 = io.open(os.path.join(D5, fn), encoding='utf-8', newline='').read()
        has_prompt = prompt in t6
        s5, s6 = parse(t5), parse(t6)
        sid_same = [x['sid'] for x in s5] == [x['sid'] for x in s6]
        diffo = [b['sid'] for a, b in zip(s5, s6) if a['o'] != b['o']]
        difft = [b['sid'] for a, b in zip(s5, s6) if a['t'] != b['t']]
        mism = []
        for b in s6:
            book, chunk = b['src'].split('/')
            if out_arr(book, chunk)[b['seg'] - 1].strip() != b['t']:
                mism.append(b['sid'])
        print('%-16s 段%-3d prompt=%s 段號一致=%s 原文異=%d 譯文異=%d 與out不符=%d %s'
              % (fn, len(s6), has_prompt, sid_same, len(diffo), len(difft), len(mism), mism))
        print('                 譯文更新段：%s' % ','.join(difft))
        tot += len(s6)
        bad += (0 if has_prompt else 1) + len(diffo) + len(mism) + (0 if sid_same else 1)
    print('files %d  total segs %d  problems %d' % (len(os.listdir(D6)), tot, bad))


if __name__ == '__main__':
    main()
