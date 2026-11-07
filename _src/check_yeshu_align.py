# -*- coding: utf-8 -*-
"""檢查業疏 out 與分卷的段落是否對得上（用書名、引文當錨點）。"""
import os, io, re, glob, collections, sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, 'TXT_分卷', '03_業疏')
OUT = os.path.join(B, 'AI語譯', 'out', '03_業疏')

TOK = re.compile(r'「([^」]{2,20})」|《([^》]{1,20})》')


def toks(s):
    r = []
    for m in TOK.finditer(s):
        t = (m.group(1) or m.group(2) or '').strip()
        if len(t) >= 2:
            r.append(t)
    return r


def main():
    print('%-16s %5s %6s %8s %s' % ('chunk', '段', '錨點', '命中', '模態位移'))
    bad = []
    for f in sorted(glob.glob(os.path.join(SRC, '*.txt'))):
        ch = os.path.splitext(os.path.basename(f))[0]
        src = [x.strip() for x in io.open(f, encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tp = os.path.join(OUT, ch + '.txt')
        if not os.path.exists(tp):
            continue
        tr = [x for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
        n = min(len(src), len(tr))
        total = hit = 0
        offs = []
        for i in range(n):
            ts = toks(tr[i])
            if not ts:
                continue
            total += len(ts)
            same = sum(1 for t in ts if t in src[i])
            hit += same
            if same == 0:
                # 找最近哪一段含這些錨點
                for j in range(max(0, i - 60), min(len(src), i + 61)):
                    if j != i and any(t in src[j] for t in ts):
                        offs.append(j - i)
                        break
        score = hit / total if total else 1.0
        mode = collections.Counter(offs).most_common(1)
        mo = '%+d x%d' % (mode[0][0], mode[0][1]) if mode else '-'
        if score < 0.5 and total >= 5:
            bad.append(ch)
        print('%-16s %5d %6d %7.0f%% %s' % (ch, n, total, score * 100, mo))
    print('\n疑似錯位 chunk %d 個：%s' % (len(bad), ', '.join(bad)))


if __name__ == '__main__':
    main()
