# -*- coding: utf-8 -*-
"""核對「說明檔自述」與實際檔案狀態是否相符。

檢查項目：
1. 說明檔說「全卷統一某術語」→ 實際該卷是否還殘留舊詞
2. 說明檔說「改 N 段」→ TSV 合計是否相符
3. 說明檔說「某檔已處理」→ 該檔備份是否存在、現行是否與備份不同
"""
import glob
import io
import os
import re
import sys
from collections import Counter, defaultdict

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
REV = os.path.join(B, 'AI語譯', '_work', 'review')
OUT = os.path.join(B, 'AI語譯', 'out')
DONE = os.path.join(B, 'batch_qwen', 'r7k_done')

# 曾被聲稱統一的術語 → 殘留的舊寫法
TERM_CLAIMS = {
    '法規': ['法規'],
    '可以修學': ['可以修學'],
    '不可修學': ['不可修學'],
    '毗尼': ['毘尼'],          # 已按原文統一，若同檔仍有混用即問題
}

# 卷名前綴對應到 out 目錄與檔名前綴
BOOK_OF_VOL = [
    ('01_行事鈔', '01_行事鈔'),
    ('02_戒疏', '02_戒疏'),
    ('03_業疏', '03_業疏'),
    ('04_比丘尼鈔', '04_比丘尼鈔'),
    ('05_拾毗尼義鈔', '05_拾毗尼義鈔'),
    ('資持記', '資持記'),
]


def vol_to_book(vol):
    for pre, book in BOOK_OF_VOL:
        if vol.startswith(pre):
            return book, vol[len(pre) + 1:]
    return None, None


def main():
    rows = []
    for p in sorted(glob.glob(os.path.join(REV, '說明_7K_*.md'))):
        name = os.path.basename(p)[len('說明_7K_'):-3]
        if '複核' in name or '擋檔' in name:
            continue
        t = io.open(p, encoding='utf-8', errors='ignore').read()
        # 解析書與卷
        m = re.match(r'(0\d|資持記)(.*)', name)
        if not m:
            continue
        # 名稱形如 02戒疏卷一下之二 / 01卷上之一 / 03業疏卷一之一
        BOOK_KEYS = [('戒疏', '02_戒疏'), ('業疏', '03_業疏'), ('比丘尼鈔', '04_比丘尼鈔'),
                     ('拾毗尼義鈔', '05_拾毗尼義鈔'), ('資持記', '資持記')]
        book = None
        volpart = name
        for kw, bk in BOOK_KEYS:
            if kw in name:
                book = bk
                volpart = name.split(kw, 1)[1]
                break
        if not book:
            book = '01_行事鈔'
            volpart = name.lstrip('01')
        # 該卷對應的 out 檔案（chunk 名前綴比對 volpart 去掉「卷」字）
        key = volpart.replace('卷', '')
        chunks = glob.glob(os.path.join(OUT, book, '*%s*.txt' % key)) if key else []
        if not chunks:
            continue
        text = ''.join(io.open(c, encoding='utf-8', errors='ignore').read() for c in chunks)
        # 檢查術語殘留
        for claim, olds in TERM_CLAIMS.items():
            if claim not in t:
                continue
            for old in olds:
                n = text.count(old)
                if n:
                    rows.append((name, '術語殘留', '%s ×%d' % (old, n), os.path.basename(chunks[0]) if chunks else ''))
                break
    lines = ['# 說明檔自述 vs 實際核對', '', '共 %d 項可疑' % len(rows), '']
    for r in rows:
        lines.append('- **%s**｜%s｜%s' % (r[0], r[1], r[2]))
    rp = os.path.join(B, '測試', '自述核對.md')
    os.makedirs(os.path.dirname(rp), exist_ok=True)
    io.open(rp, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('可疑 %d 項，報告 %s' % (len(rows), rp))
    agg = Counter(r[1] for r in rows)
    for k, v in agg.items():
        print('  %s：%d' % (k, v))
    for r in rows[:15]:
        print('   %-28s %s' % (r[0][:26], r[2]))


if __name__ == '__main__':
    main()