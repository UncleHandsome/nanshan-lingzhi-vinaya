# -*- coding: utf-8 -*-
"""黃金 50 段 v2：單段材料（每段一份 .md／.json）＋對照層。

規格（2026-11-22 使用者指示）：
  - 單段送審，不做 10 段大包；前文 ≤1800 字、後文 ≤600 字。
  - 尼鈔：原典雙行夾注（display_source〔…〕，CBETA X40n0724）。
  - 行事鈔：mother_corpus.ji_for_chao() 的【資持記相關釋文】。
  - 義鈔：補標點原文＋戒疏／行宗記等平行釋文（輔要記書庫無檔，掛現有可用者）。
  - 業疏／戒疏：單邊記文附【所釋疏文】＋科判；前文帶到前一段（如《周禮》九拜）。
  - 雙欄逐段對位（mk_reaudit._parts_of 保留 lab/source/translation）。

輸出：重作材料_長段/回歸50v2/_再審/<book_id>_<key>.md + .json
     重作材料_長段/回歸50v2/_再審/_材料索引.md、索引.json、_原文核驗.md

用法：
  python -X utf8 _src/mk_golden50v2.py --dry-run
  python -X utf8 _src/mk_golden50v2.py
"""
import argparse
import io
import json
import os
import re
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
sys.path.insert(0, os.path.join(B, '_src'))
import mk_reaudit_materials as RA  # noqa: E402

SAMPLE = os.path.join(B, '重作材料_長段', '五書抽樣10')
ROOT = os.path.join(B, '重作材料_長段', '回歸50v2')
OUT = os.path.join(ROOT, '_再審')
BOOKS = [('尼鈔', 'nicao'), ('行事鈔', 'xingshichao'), ('義鈔', 'yichao'),
         ('業疏', 'yeshu'), ('戒疏', 'jieshu')]
PRE_CAP = 1800
POST_CAP = 600


def _keys(book):
    t = io.open(os.path.join(SAMPLE, '%s_抽樣10.md' % book), encoding='utf-8').read()
    ks = [x.strip() for x in re.findall(r'- key：(.+)', t)]
    if len(ks) != 10:
        raise SystemExit('%s 抽樣 key 數 %d ≠ 10' % (book, len(ks)))
    return ks


def main():
    ap = argparse.ArgumentParser(description='黃金 50 段 v2 單段材料')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    keys = {b: _keys(b) for b, _ in BOOKS}
    os.makedirs(ROOT, exist_ok=True)
    io.open(os.path.join(ROOT, 'keys.json'), 'w', encoding='utf-8').write(
        json.dumps(keys, ensure_ascii=False, indent=1))
    if args.dry_run:
        for b, _ in BOOKS:
            print('%s：%d keys' % (b, len(keys[b])))
        return
    all_meta = []
    for book, bid in BOOKS:
        print('== %s ==' % book)
        st = RA.generate_single(book, OUT, keys[book], pre_cap=PRE_CAP,
                                post_cap=POST_CAP, check_raw=False, force=True)
        for m in st['packs']:
            m['book'] = book
            m['book_id'] = bid
            all_meta.append(m)
    # 合併索引
    json.dump({'generated': RA._now(), 'single': True, 'pre_cap': PRE_CAP,
               'post_cap': POST_CAP, 'n': len(all_meta), 'keys': keys,
               'packs': [{k: m.get(k) for k in
                          ('key', 'sample_key', 'book', 'book_id', 'vol', 'chunk',
                           'raw_start', 'raw_end', 'chars', 'md_chars', 'refs')}
                         for m in all_meta]},
              io.open(os.path.join(OUT, '索引.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    # 索引 md（_ 開頭，qwen 不會送）
    L = ['# 黃金 50 段 v2 單段材料索引', '',
         '- 來源：`定稿/<book>.jsonl`（只讀）；每段一份 `.md`／`.json`。',
         '- 前文 ≤%d 字、後文 ≤%d 字；對照層依書別掛載。' % (PRE_CAP, POST_CAP), '',
         '| # | 書 | key | 卷 | 原文 | 現譯 | md 字數 | 對照層 |',
         '|--:|:--|:--|:--|--:|--:|--:|:--|']
    for n, m in enumerate(all_meta, 1):
        L.append('| %d | %s | %s | %s | %d | %d | %d | %s |'
                 % (n, m['book'], m.get('sample_key'), m.get('vol'),
                    m['chars']['src'], m['chars']['tr'], m['md_chars'],
                    '、'.join(m.get('refs') or []) or '—'))
    io.open(os.path.join(OUT, '_材料索引.md'), 'w', encoding='utf-8').write(
        '\n'.join(L) + '\n')
    # 原文核驗
    bad = [m for m in all_meta if m.get('raw_ok') is False]
    badparts = [m for m in all_meta if m.get('parts_joined') is False]
    C = ['# 黃金 50 段 v2 原文核驗', '',
         '- 單位：%d；source==raw 失敗：%d；parts 拼接不一致：%d。'
         % (len(all_meta), len(bad), len(badparts)), '']
    for m in all_meta:
        C.append('- %s %s｜%s｜raw %s-%s｜source==raw：%s｜parts 拼接：%s'
                 % (m['book'], m.get('sample_key'), m.get('vol'),
                    m.get('raw_start'), m.get('raw_end'),
                    'OK' if m.get('raw_ok') else 'FAIL',
                    'OK' if m.get('parts_joined') is not False else 'NOTE'))
    io.open(os.path.join(OUT, '_原文核驗.md'), 'w', encoding='utf-8').write(
        '\n'.join(C) + '\n')
    md = [m['md_chars'] for m in all_meta]
    print('\n共 %d 份；md 字數 最小 %d／中位 %d／最大 %d'
          % (len(all_meta), min(md), sorted(md)[len(md) // 2], max(md)))
    refcnt = {}
    for m in all_meta:
        for t in m.get('refs') or []:
            k = t.split('（')[0]
            refcnt[k] = refcnt.get(k, 0) + 1
    print('對照層：', refcnt)
    print('source 失敗 %d、parts NOTE %d' % (len(bad), len(badparts)))


if __name__ == '__main__':
    main()
