# -*- coding: utf-8 -*-
"""第一優先南山親註（2026-11-22）：書庫接線最小 smoke test。

只讀、不呼叫 qwen、不寫定稿。檢查三件事：
  A. 11 部書都已進 原文/ 且被 local_corpus 索引（行數、漢字數）
  B. local_corpus.find 對每一部書都能命中（取書中段原文自查）
  C. 《義鈔》材料會掛【義鈔輔要記相關釋文】區塊

用法：
  python -X utf8 _src/test_priority1_corpus.py
  python -X utf8 _src/test_priority1_corpus.py --full   # 另產 1 份義鈔材料到 _tmp_smoke/
"""
import argparse
import io
import os
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import local_corpus as LC  # noqa: E402
import mk_reaudit_materials as MR  # noqa: E402

# 書名 → 原文檔名（不含 .txt）
EXPECT = {
    '義鈔輔要記': '四分律拾毗尼義鈔輔要記',
    '毗尼討要': '毗尼討要',
    '四分律行事鈔簡正記': '四分律行事鈔簡正記',
    '四分律隨機羯磨疏正源記': '四分律隨機羯磨疏正源記',
    '四分律含注戒本疏發揮記': '四分律含注戒本疏發揮記',
    '芝苑遺編': '芝苑遺編',
    '量處輕重儀': '量處輕重儀',
    '釋門歸敬儀': '釋門歸敬儀',
    '教誡新學比丘行護律儀': '教誡新學比丘行護律儀',
    '釋門章服儀': '釋門章服儀',
    '佛制比丘六物圖': '佛制比丘六物圖',
}

FAILS = []


def check(ok, msg):
    print(('  ✓ ' if ok else '  ✗ ') + msg)
    if not ok:
        FAILS.append(msg)


def pick_query(book):
    """取書中段一行原文，回傳 14 個漢字（去標點）作查詢詞。"""
    lines = [x.strip() for x in
             io.open(LC._flat_file(book), encoding='utf-8').read().split('\n') if x.strip()]
    cands = [x for x in lines[3:] if len(LC._plain(x)) >= 20 and '〔' not in x]
    if not cands:
        return ''
    h = LC._plain(cands[len(cands) // 2])
    return h[:14]


def part_a():
    print('A. 原文/ 與索引')
    for book, fn in EXPECT.items():
        p = os.path.join(B, '原文', fn + '.txt')
        ok = os.path.isfile(p)
        check(ok, '%s：原文/%s.txt %s' % (book, fn, '存在' if ok else '缺檔'))
        if not ok:
            continue
        rows = LC.BOOK_LINES.get(book) or []
        han = sum(len(MR.han(LC.LINES[i]['text'])) for i in rows)
        check(len(rows) >= 100 and han >= 3000,
              '%s：索引 %d 行／%d 漢字' % (book, len(rows), han))
        check(book in LC.BOOK_BLOB, '%s：已在 BOOK_BLOB' % book)


def part_b():
    print('B. local_corpus.find 命中')
    for book in EXPECT:
        q = pick_query(book)
        if not q:
            check(False, '%s：取不到查詢詞' % book)
            continue
        hits = LC.find(q, book, limit=1, pad=120)
        got = (hits[0].get('book') if hits else None)
        ok = got == book
        check(ok, '%s：find("%s", work=%s) → %s'
              % (book, q[:8] + '…', book, got or '無命中'))
        if ok:
            print('      %s｜%s' % (hits[0].get('juan'),
                                    (hits[0].get('kwic') or '').replace('\n', ' ')[:70]))


def part_c(full=False):
    print('C. 義鈔材料掛【義鈔輔要記相關釋文】')
    raw = MR.load_raw('義鈔')[0]
    order = MR.make_units('義鈔', raw)
    target = None
    for i, u in enumerate(order):
        src = MR._plain_src(u)
        if len(MR.han(src)) < 40:
            continue
        if MR._fuyao_note(src):
            target = (i, u)
            break
    check(target is not None, '義鈔 509 段中找得到輔要記同段釋文')
    if target is None:
        return
    i, u = target
    title_hit, body = '', ''
    for title, b in MR.reference_blocks('義鈔', u, order, i):
        if '義鈔輔要記相關釋文' in title:
            title_hit, body = title, b
            break
    check(bool(title_hit), 'reference_blocks 回傳標題含「義鈔輔要記相關釋文」')
    check(len(body) > 60, '輔要記區塊內文 %d 字（非空）' % len(body))
    if title_hit:
        print('      單位 %s｜%s' % (u['key'], title_hit))
        print('      ' + body.replace('\n', ' ')[:120] + '…')

    if full:
        outdir = os.path.join(B, '_tmp_smoke', 'yichao_fuyao')
        print('  產生 1 份實際材料 → %s' % os.path.relpath(outdir, B))
        import json
        keys = os.path.join(B, '_tmp_smoke', 'keys.json')
        os.makedirs(os.path.dirname(keys), exist_ok=True)
        io.open(keys, 'w', encoding='utf-8').write(
            json.dumps({'義鈔': [u['key']]}, ensure_ascii=False))
        MR.generate_single('義鈔', outdir, [u['key']], force=True, verbose=False)
        md = [f for f in os.listdir(outdir) if f.endswith('.md')]
        txt = ''.join(io.open(os.path.join(outdir, f), encoding='utf-8').read()
                      for f in md)
        check('義鈔輔要記相關釋文' in txt, '實際 .md 材料含「義鈔輔要記相關釋文」')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--full', action='store_true', help='另產 1 份義鈔材料驗證')
    args = ap.parse_args()
    LC.load()
    print('書庫：%d 書／%d 行' % (len(LC.BOOK_BLOB), len(LC.LINES)))
    print()
    part_a()
    print()
    part_b()
    print()
    part_c(full=args.full)
    print()
    if FAILS:
        print('FAIL：%d 項' % len(FAILS))
        for f in FAILS:
            print('  - ' + f)
        return 1
    print('PASS：全部通過')
    return 0


if __name__ == '__main__':
    sys.exit(main())
