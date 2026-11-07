# -*- coding: utf-8 -*-
"""把句讀檔的標點投影回分卷（業疏）：輸出不改字、只加標點的分卷。

用法：python _src/punctuate_yeshu.py
輸出：TXT_分卷_標點/03_業疏/*.txt（與分卷同段數）
"""
import os, io, re, difflib, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, 'TXT_分卷', '03_業疏')
JU = os.path.join(B, 'TXT_句讀', '03_業疏')
OUT = os.path.join(B, 'TXT_分卷_標點', '03_業疏')
HAN = re.compile(r'[\u4e00-\u9fa5]')


def han_only(s):
    return ''.join(HAN.findall(s))


def load(p, skip):
    return [x.strip() for x in io.open(p, encoding='utf-8').read().split('\n')[skip:] if x.strip()]


def build_map(a, b):
    """a,b 為漢字串；回傳 a 位置 → b 位置（只記相等區塊）。"""
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    pos = {}
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for k in range(i2 - i1):
                pos[i1 + k] = j1 + k
    return pos


def main():
    os.makedirs(OUT, exist_ok=True)
    total = exact = 0
    report = []
    for f in sorted(glob.glob(os.path.join(SRC, '*.txt'))):
        ch = os.path.splitext(os.path.basename(f))[0]
        src = load(f, 5)
        jp = os.path.join(JU, ch + '.txt')
        if not os.path.exists(jp):
            report.append((ch, len(src), 0, 'no-ju'))
            continue
        ju_text = '\n'.join(load(jp, 4))
        # 漢字索引 → 原始字元索引
        raw_pos = [m.start() for m in HAN.finditer(ju_text)]
        a = han_only(''.join(src))
        b = han_only(ju_text)
        pos = build_map(a, b)
        out_paras, ok = [], 0
        ai = 0
        for p in src:
            n = len(han_only(p))
            mapped = [pos.get(ai + k) for k in range(n)]
            ai += n
            if any(m is None for m in mapped):
                out_paras.append(p)
                continue
            s, e = raw_pos[mapped[0]], raw_pos[mapped[-1]] + 1
            seg = ju_text[s:e]
            seg = re.sub(r'[\r\n\u3000]+', '', seg).strip()
            if han_only(seg) == han_only(p):
                out_paras.append(seg)
                ok += 1
            else:
                out_paras.append(p)
        total += len(src)
        exact += ok
        io.open(os.path.join(OUT, ch + '.txt'), 'w', encoding='utf-8').write('\n\n'.join(out_paras) + '\n')
        report.append((ch, len(src), ok, '%.0f%%' % (100.0 * ok / max(1, len(src)))))
    print('paragraphs', total, 'punctuated', exact, '%.1f%%' % (100.0 * exact / max(1, total)))
    low = [r for r in report if isinstance(r[2], int) and r[2] < 0.8 * r[1]]
    print('低於 80%% 的 chunk：')
    for r in low:
        print('  ', r)


if __name__ == '__main__':
    main()
