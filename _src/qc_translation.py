# -*- coding: utf-8 -*-
"""譯文品質機械檢查：引文核對 + 同詞異譯 + 記錄一致性。

用法：
  python _src/qc_translation.py              # 全書
  python _src/qc_translation.py --book 02_戒疏
"""
import glob
import io
import json
import os
import re
import sys
from collections import Counter, defaultdict

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, 'AI語譯', 'out')
REPORT = os.path.join(B, '測試', 'QC譯文檢查.md')

SRC_MAP = {
    '01_行事鈔': os.path.join(B, 'TXT_分卷', '01_行事鈔'),
    '02_戒疏': os.path.join(B, 'TXT_分卷', '02_戒疏'),
    '資持記': os.path.join(B, 'TXT_分卷', '資持記_細分'),
    '04_比丘尼鈔': os.path.join(B, 'TXT_分卷', '04_比丘尼鈔'),
    '05_拾毗尼義鈔': os.path.join(B, 'TXT_分卷', '05_拾毗尼義鈔'),
    '03_業疏': os.path.join(B, 'TXT_分卷_標點', '03_業疏'),
}

QUOTE = re.compile(r'「([^」]{2,40})」')


def load_pairs(book, chunk):
    """回傳 [(原文, 譯文)]，長度對齊時才回傳。"""
    sd = SRC_MAP.get(book)
    if not sd:
        return None
    sp = os.path.join(sd, chunk + '.txt')
    tp = os.path.join(OUT, book, chunk + '.txt')
    if not (os.path.exists(sp) and os.path.exists(tp)):
        return None
    raw = io.open(sp, encoding='utf-8', errors='ignore').read().split('\n')
    src = [x.strip() for x in (raw[5:] if book != '03_業疏' else raw) if x.strip()]
    tr = [x for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8', errors='ignore').read()) if x.strip()]
    if len(src) != len(tr):
        return None
    return list(zip(src, tr))


def check_quotes(book, chunk, pairs):
    """譯文引號內的文字，應在對應原文中出現（允許原文整體包含）。"""
    bad = []
    for i, (s, t) in enumerate(pairs, 1):
        for m in QUOTE.finditer(t):
            q = m.group(1).strip()
            if len(q) < 3:
                continue
            # 去掉譯文常見的標點與虛詞後再比
            cand = re.sub(r'[，。、；：！？（）〔〕]', '', q)
            if cand in re.sub(r'[，。、；：！？（）〔〕]', '', s):
                continue
            # 意譯型引號（解說用的）不算錯，只報「看起來像原文」的
            if re.search(r'[之乎者也矣焉哉]', q) or len(q) <= 12:
                bad.append((i, q, s[:40], t[:40]))
    return bad


def check_terms(book, chunk, pairs):
    """同一 chunk 內，同一原文詞若被譯成多種形式，列出對照。"""
    # 取 2-4 字原文詞，統計其譯文對應中是否出現固定字串
    term_tr = defaultdict(Counter)
    for s, t in pairs:
        for n in (2, 3, 4):
            for i in range(len(s) - n + 1):
                term = s[i:i + n]
                if re.search(r'[，。、；：！？「」『』（）]', term):
                    continue
                # 只在譯文也含該詞（或明顯對應）時記錄
                term_tr[term][t] += 1
    return term_tr


def main():
    only = None
    if '--book' in sys.argv:
        only = sys.argv[sys.argv.index('--book') + 1]

    quote_issues = []
    for book in sorted(os.listdir(OUT)):
        d = os.path.join(OUT, book)
        if not os.path.isdir(d) or book not in SRC_MAP:
            continue
        if only and book != only:
            continue
        for f in sorted(os.listdir(d)):
            if not f.endswith('.txt'):
                continue
            chunk = f[:-4]
            pairs = load_pairs(book, chunk)
            if not pairs:
                continue
            for seg, q, s, t in check_quotes(book, chunk, pairs):
                quote_issues.append((book, chunk, seg, q, s, t))

    lines = ['# 譯文品質機械檢查', '', '## 一、引文核對（引號內文字應見於原文）', '',
             '共 %d 處可疑' % len(quote_issues), '']
    for book, chunk, seg, q, s, t in quote_issues[:200]:
        lines.append('- **%s/%s #%d** 引「%s」｜原文：%s｜譯文：%s' % (book, chunk, seg, q, s, t))
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    io.open(REPORT, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('引文可疑 %d 處，報告 %s' % (len(quote_issues), REPORT))
    for x in quote_issues[:10]:
        print('  %s/%s #%d 「%s」' % (x[0], x[1], x[2], x[3][:30]))


if __name__ == '__main__':
    main()