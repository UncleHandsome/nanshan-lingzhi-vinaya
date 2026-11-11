# -*- coding: utf-8 -*-
"""將譯文段落與原文（TXT_分卷）段落做單調對齊，輸出對照，供覆核現代詞。

用法：
  python -X utf8 _src/_mw_align.py 01_行事鈔 09c_卷下之一 9 13 17
  參數：書 檔名（不帶 .txt） 譯文段號...
"""
import io, os, re, sys, difflib

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'


def load(p):
    return open(p, 'rb').read().decode('utf-8')


def norm(s):
    return re.sub(r'[^\u4e00-\u9fff]', '', s)


def bigrams(s):
    s = norm(s)
    return set(s[i:i + 2] for i in range(len(s) - 1))


def align(tr_lines, src_lines):
    """動態規劃單調對齊，回傳 tr index -> src index。"""
    n, m = len(tr_lines), len(src_lines)
    tb = [bigrams(x) for x in tr_lines]
    sb = [bigrams(x) for x in src_lines]
    NEG = -1e18
    # dp[i][j] 前 i 譯文段、前 j 原文段之最佳分數
    dp = [[NEG] * (m + 1) for _ in range(n + 1)]
    bt = [[0] * (m + 1) for _ in range(n + 1)]
    for j in range(m + 1):
        dp[0][j] = 0
    for i in range(n + 1):
        dp[i][0] = 0
    for i in range(1, n + 1):
        di = dp[i]
        dpim1 = dp[i - 1]
        bti = bt[i]
        for j in range(1, m + 1):
            # 略過原文段
            best = dpim1[j]
            arg = 1
            if dp[i][j - 1] > best:
                best = dp[i][j - 1]
                arg = 2
            a, b = tb[i - 1], sb[j - 1]
            sc = 0.0
            if a and b:
                inter = len(a & b)
                sc = inter / (len(a) ** 0.5 * len(b) ** 0.5) if inter else 0.0
            cand = dpim1[j - 1] + sc * 3.0
            if cand > best:
                best = cand
                arg = 3
            di[j] = best
            bti[j] = arg
    # 回溯
    mp = {}
    i, j = n, m
    while i > 0 and j > 0:
        a = bt[i][j]
        if a == 3:
            mp[i - 1] = j - 1
            i -= 1
            j -= 1
        elif a == 2:
            j -= 1
        else:
            i -= 1
    return mp


def main():
    book, stem = sys.argv[1], sys.argv[2]
    want = [int(x) for x in sys.argv[3:]]
    trp = os.path.join(B, 'AI語譯', 'out', book, stem + '.txt')
    srcp = os.path.join(B, 'TXT_分卷', book, stem + '.txt')
    tr = re.split(r'\r?\n', load(trp))
    src = [l for l in re.split(r'\r?\n', load(srcp))]
    # 原文略過書首資訊 3 行
    src = src[3:]
    trn = [x for x in tr]
    mp = align(trn, src)
    for w in want:
        i = w - 1
        print('=' * 70)
        print('【譯文 %s:%d】' % (stem, w))
        print(trn[i] if 0 <= i < len(trn) else '(無)')
        print('-' * 70)
        if i in mp:
            j = mp[i]
            print('【原文 %s 第%d行】' % (stem, j + 1 + 3))
            print(src[j])
        else:
            print('【原文】未對到')
        print()


if __name__ == '__main__':
    main()
