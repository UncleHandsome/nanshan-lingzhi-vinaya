# -*- coding: utf-8 -*-
"""缺口盲翻合流檢查：BLIND-*／GAP-* 必須先過 build_a2＋qc_scan 的同一組門檻。

背景：缺口盲翻曾直接寫進 定稿/<book>.jsonl，繞過 build_a2 的段別標籤檢查與
qc_scan 的殘留物掃描，導致 label 仍是「疏文」、譯文沒有【鈔文】、檔頭污染
（``` ／--- START OF FILE）留在正文裡。

用法：
  python -X utf8 _src/check_final_merge.py --book 尼鈔
  python -X utf8 _src/check_final_merge.py --book 尼鈔 --all
  python -X utf8 _src/check_final_merge.py --book 尼鈔 --reply-dir 重作材料_長段/尼鈔_缺口盲翻/回覆
"""
import argparse
import io
import json
import os
import re
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
sys.path.insert(0, os.path.join(B, '_src'))
import book_config as BC  # noqa: E402

BOOKS = {'業疏': 'yeshu', '戒疏': 'jieshu', '尼鈔': 'nicao',
         '行事鈔': 'xingshichao', '義鈔': 'yichao', '資持記': 'zhichi'}
LABELS = ('疏文', '記文', '鈔文', '律文', '註文', '序文')
GAP_PREFIX = ('BLIND-', 'GAP')
JUNK = re.compile(r'---\s*START OF FILE|```\s*\n|【原文】|【待審譯文】|【前文背景|'
                  r'(?:local_search|web_search|web_fetch)\s*\(')


def _rows(path):
    return [json.loads(x) for x in io.open(path, encoding='utf-8') if x.strip()]


def check_rows(book, all_rows=False):
    bid = BOOKS[book]
    p = os.path.join(B, '定稿', bid + '.jsonl')
    if not os.path.exists(p):
        return ['NOFILE %s' % p], 0, 0
    unit = BC.cfg(book).get('unit') or '鈔文'
    rows = _rows(p)
    hard, warn = [], []
    n = 0
    for r in rows:
        k = r.get('key') or ''
        if not all_rows and not k.startswith(GAP_PREFIX):
            continue
        n += 1
        hard_k, warn_k = [], []
        if r.get('label') != unit:
            hard_k.append('label=%s（應為 %s）' % (r.get('label'), unit))
        tr = r.get('translation') or ''
        if not re.match(r'^\s*【(%s)】' % '|'.join(LABELS), tr):
            hard_k.append('譯文開頭無合法段別標籤')
        elif not tr.lstrip().startswith('【%s】' % unit):
            hard_k.append('譯文標籤不是【%s】' % unit)
        if JUNK.search(tr):
            hard_k.append('殘留檔頭／工具／材料標記')
        src = r.get('source') or ''
        if tr.count('〔') > src.count('〔'):
            (hard_k if k.startswith('BLIND-') else warn_k).append(
                '譯文〔〕多於原文（%d>%d）' % (tr.count('〔'), src.count('〔')))
        if tr.rstrip().endswith(('：', ':')):
            (hard_k if k.startswith('BLIND-') else warn_k).append('譯文結尾為冒號')
        for s in (r.get('segments') or []):
            if s.get('label') != unit:
                hard_k.append('segment label=%s' % s.get('label'))
            if (s.get('source') or '') != src:
                warn_k.append('segment source 與頂層不一致')
            if re.match(r'^\s*【%s】' % unit, s.get('translation') or ''):
                warn_k.append('segment 譯文重複段別標籤')
        if hard_k:
            hard.append('%s：%s' % (k, '；'.join(sorted(set(hard_k)))))
        if warn_k:
            warn.append('%s：%s' % (k, '；'.join(sorted(set(warn_k)))))
    return hard, n, warn


def check_replies(book, rel):
    unit = BC.cfg(book).get('unit') or '鈔文'
    d = os.path.join(B, rel.replace('/', os.sep))
    bad = []
    if not os.path.isdir(d):
        return ['NOFILE %s' % d]
    for f in sorted(os.listdir(d)):
        if not f.endswith('_回.txt'):
            continue
        t = io.open(os.path.join(d, f), encoding='utf-8').read()
        if not t.strip():
            bad.append('%s：空白回覆' % f)
        if JUNK.search(t):
            bad.append('%s：殘留檔頭／工具／材料標記' % f)
        if re.search(r'(?m)^【(?:疏文|記文|律文|註文|序文)】', t):
            bad.append('%s：混入非本段標籤' % f)
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--book', required=True, choices=sorted(BOOKS))
    ap.add_argument('--all', action='store_true', help='連非缺口段一併檢查（只報不擋）')
    ap.add_argument('--reply-dir', default='')
    args = ap.parse_args()

    hard, n, warn = check_rows(args.book, args.all)
    if args.reply_dir:
        for x in check_replies(args.book, args.reply_dir):
            hard.append('回覆：' + x)
    print('檢查 %d 段｜硬傷 %d｜提醒 %d' % (n, len(hard), len(warn)))
    for x in hard[:40]:
        print('  ✗', x)
    for x in warn[:20]:
        print('  ⚠', x)
    if hard:
        print('缺口盲翻未通過合流門檻，不得寫入定稿')
        raise SystemExit(1)
    print('缺口盲翻合流檢查通過')


if __name__ == '__main__':
    main()
