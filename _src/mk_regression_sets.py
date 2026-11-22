# -*- coding: utf-8 -*-
"""回歸測試清單產生器：負樣本 20 段 ＋ 盲測 25 段（只產清單，不跑 qwen）。

用途（reaudit2.txt §四）：
  1. 負樣本 20 段（防誤殺）：原文真的含高危詞／夾注，但譯文本來就正確的段落。
     用來量 REAUDIT 的假 FIX 率（>20% 即提示詞過嚴）與 VERIFY 誤判率。
  2. 盲測 25 段（泛化）：五書各 5 段，完全沒參與提示詞設計（排除黃金 50 段），
     人工快檢新錯誤類型是否仍抓得到、且沒製造新硬傷。

選段是確定性的（md5(key) 排序），可重跑得到同一份清單；只讀 `定稿/*.jsonl`，
輸出到 `重作材料_長段/回歸測試/`，不寫定稿、不產正式材料、不呼叫 qwen。

用法：
  python -X utf8 _src/mk_regression_sets.py --dry-run
  python -X utf8 _src/mk_regression_sets.py
  python -X utf8 _src/mk_regression_sets.py --out 重作材料_長段/回歸測試
"""
import argparse
import hashlib
import io
import json
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
import sys
sys.path.insert(0, os.path.join(B, '_src'))
import recheck_scan as RC  # noqa: E402  共用具體詞旗標與 FATAL 定義

BOOKS = {'尼鈔': 'nicao', '行事鈔': 'xingshichao', '義鈔': 'yichao',
         '業疏': 'yeshu', '戒疏': 'jieshu'}
SAMPLE_DIR = '重作材料_長段/五書抽樣10'
NEG_PER_BOOK = 4
BLIND_PER_BOOK = 5
# 負樣本只排除「譯文本身壞掉」的旗標；source 邊界與標籤慣例正是要測 REAUDIT 會不會誤殺
_NEG_BLOCK = {'EMPTY_TR', 'MISSING_FIELD', 'DUAL_MISSING_COL', 'BG_LEAK'}
_HAN = re.compile(r'[\u4e00-\u9fff]')


def han(s):
    return ''.join(_HAN.findall(s or ''))


def _rows(book):
    p = os.path.join(B, '定稿', BOOKS[book] + '.jsonl')
    out = []
    for line in io.open(p, encoding='utf-8'):
        if line.strip():
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out


def golden_keys():
    """黃金 50 段（抽樣10）的 key，盲測必須排除。"""
    d = os.path.join(B, SAMPLE_DIR.replace('/', os.sep))
    ks = set()
    if not os.path.isdir(d):
        return ks
    for f in os.listdir(d):
        if not f.endswith('.md'):
            continue
        t = io.open(os.path.join(d, f), encoding='utf-8').read()
        ks.update(re.findall(r'key[：:]\s*(\S+)', t))
    return ks


def _h(key):
    return hashlib.md5((key or '').encode('utf-8')).hexdigest()


def _triggers(book, src):
    ff = [w for w in RC.FALSE_FRIEND if w in src]
    bt = [w for w in RC.BOOK_TERMS.get(book, ()) if w in src]
    return ff, bt


def build(verbose=True):
    gold = golden_keys()
    neg, blind = [], []
    extra = {}
    for book in BOOKS:
        rows = _rows(book)
        cands = []
        for r in rows:
            key = str(r.get('key') or '')
            src = r.get('source') or ''
            tr = r.get('translation') or ''
            if not key or not han(tr) or key in gold:
                continue
            sh = len(han(src))
            if sh < 60:
                continue
            scan = RC.scan_row(book, r)
            fatal = [f for f in scan['flags'] if f in _NEG_BLOCK]
            if fatal:
                continue
            ff, bt = _triggers(book, src)
            if ff or bt:
                cands.append({'book': book, 'key': key, 'row': r, 'src': src,
                              'tr': tr, 'src_han': sh,
                              'triggers': (ff + bt)[:4], 'flags': scan['flags']})
        cands.sort(key=lambda x: _h(x['key']))
        used_words, picked = set(), []
        for c in cands:
            if len(picked) >= NEG_PER_BOOK:
                break
            new = [w for w in c['triggers'] if w not in used_words]
            if not new and len(picked) >= 2:
                continue
            used_words.update(new)
            picked.append(c)
        neg.extend(picked)
        # 盲測：純 md5 排序，排除黃金與負樣本
        _neg_keys = {c['key'] for c in picked}
        pool = []
        for r in rows:
            key = str(r.get('key') or '')
            if not key or key in gold or key in _neg_keys:
                continue
            if len(han(r.get('source'))) < 80 or not han(r.get('translation')):
                continue
            pool.append(r)
        pool.sort(key=lambda r: _h(str(r.get('key'))))
        for r in pool[:BLIND_PER_BOOK]:
            blind.append({'book': book, 'key': str(r.get('key')),
                          'row': r, 'src': r.get('source') or '',
                          'tr': r.get('translation') or '',
                          'src_han': len(han(r.get('source'))),
                          'triggers': [], 'flags': []})
        if verbose:
            print('%-5s 負樣本候選 %4d → 取 %d；盲測取 %d'
                  % (book, len(cands), len(picked),
                     min(BLIND_PER_BOOK, len(pool))))
        extra[book] = [c for c in cands if c['key'] not in {x['key'] for x in picked}]
    # 某書候選不足時，由其他書補足 20 段（保持跨書分佈，不硬湊同段）
    picked_keys = {x['key'] for x in neg}
    if len(neg) < 5 * NEG_PER_BOOK:
        pool = []
        for book in BOOKS:
            pool.extend(extra.get(book, []))
        pool.sort(key=lambda x: _h(x['key']))
        for c in pool:
            if len(neg) >= 5 * NEG_PER_BOOK:
                break
            if c['key'] in picked_keys:
                continue
            picked_keys.add(c['key'])
            neg.append(c)
    return neg, blind


def _table(items, with_trigger=True):
    head = ['| # | 書 | key | 卷 | 原文起頭 | 漢字 | 譯文漢字 |'
            + (' 觸發詞 |' if with_trigger else '')]
    sep = ['|--:|:--|:--|:--|:--|--:|--:|' + (' :--|' if with_trigger else '')]
    L = head + sep
    for i, x in enumerate(items, 1):
        src = (x['src'] or '').replace('\n', ' ').replace('|', '｜')
        vol = (x['row'].get('vol') or '').replace('|', '｜')
        line = ('| %d | %s | %s | %s | %s… | %d | %d |'
                % (i, x['book'], x['key'], vol, src[:34], x['src_han'], len(han(x['tr']))))
        if with_trigger:
            line += ' %s |' % ('、'.join(x['triggers']) or '—')
        L.append(line)
    return L


def write_all(outdir, neg, blind, generated):
    os.makedirs(outdir, exist_ok=True)
    head = ['# 負樣本 20 段（防誤殺對照組）', '',
            '- 產生時間：%s' % generated,
            '- 來源：`定稿/*.jsonl`（只讀）；黃金 50 段已排除。',
            '- 選法：原文含高危詞／具體詞旗標、無致命旗標、md5(key) 排序，五書各 4 段。',
            '- 用途：跑新管線後量 (1) REAUDIT 假 FIX 率（>20% 代表提示詞過嚴）；'
            '(2) VERIFY 是否把正當駁回誤判 RETRY。',
            '- **人工先確認每段譯文本來正確**；若原譯有錯，該段不列入負樣本分母。', '']
    head += _table(neg)
    head += ['', '## 判讀', '',
             '- 假 FIX 率 = 判 FIX 的負樣本數／20。',
             '- VERIFY 誤判率 = 正當駁回（未改動或合法未改）卻被判 RETRY 的比例。',
             '- 兩項任一超標 → 先調整提示詞或 recheck_scan 旗標，不得直接放量。', '']
    io.open(os.path.join(outdir, '負樣本20.md'), 'w', encoding='utf-8').write('\n'.join(head))

    head = ['# 盲測 25 段（Out-of-Sample 泛化）', '',
            '- 產生時間：%s' % generated,
            '- 來源：`定稿/*.jsonl`（只讀）；已排除黃金 50 段與負樣本。',
            '- 選法：md5(key) 排序，五書各 5 段（非挑錯，避免人為偏差）。',
            '- 用途：確認提示詞對「沒寫進設計的新錯誤類型」仍有效，且沒製造新硬傷。',
            '- 驗收：人工逐段快檢；不得只看 FIX 數。', '']
    head += _table(blind, with_trigger=False)
    head += ['', '## 判讀', '',
             '- 記錄每段：抓到／漏掉／誤殺（原本正確卻判 FIX）。',
             '- 若出現新型錯誤但 REAUDIT 未抓 → 補的是**抽象規則**，不是把該詞寫進提示詞；'
             '若該詞可程式判定，才加進 `recheck_scan.py` 旗標。',
             '- 若出現誤殺 → 檢查是否屬「合理顯義／必要消歧」，恢復護欄而非放寬全部。', '']
    io.open(os.path.join(outdir, '盲測25.md'), 'w', encoding='utf-8').write('\n'.join(head))

    io.open(os.path.join(outdir, '跑法.md'), 'w', encoding='utf-8').write(
        '\n'.join([
            '# 回歸測試跑法（不跑 qwen 時先看這份）', '',
            '## 一、黃金 50 段', '',
            '題目在 `重作材料_長段/五書抽樣10/`，標準答案卷為五份專家清單。',
            '三條件：召回 100%、無副作用、成本可控（詳見 AGENTS 7A.7b）。', '',
            '## 二、負樣本 20 段', '',
            '`負樣本20.md` 逐段確認原譯正確後，走新版 `mk_audit_materials`／`REAUDIT`：',
            '假 FIX 率 >20% 即代表提示詞或旗標過嚴；VERIFY 誤打正當駁回亦須統計。', '',
            '## 三、盲測 25 段', '',
            '`盲測25.md` 不含標準答案，逐段人工快檢；新錯誤只能回饋成抽象規則或程式旗標。', '',
            '## 四、禁止', '',
            '- 不可把本清單的具體詞例抄回提示詞（詞例只存在 `recheck_scan.py`）。',
            '- 不可用盲測結果逐段硬修提示詞（會再次過擬合）。',
            '- 未過負樣本前不得全量跑批。', '']))

    io.open(os.path.join(outdir, '索引.json'), 'w', encoding='utf-8').write(
        json.dumps({'generated': generated,
                    'negative': [{'book': x['book'], 'key': x['key'],
                                  'triggers': x['triggers']} for x in neg],
                    'blind': [{'book': x['book'], 'key': x['key']} for x in blind]},
                   ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser(
        description='產出負樣本 20／盲測 25 清單（只讀定稿、不跑 qwen）')
    ap.add_argument('--out', default='重作材料_長段/回歸測試')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    neg, blind = build()
    print('負樣本 %d 段；盲測 %d 段' % (len(neg), len(blind)))
    if args.dry_run:
        print('（--dry-run：未寫檔）')
        return
    import datetime
    out = args.out if os.path.isabs(args.out) else os.path.join(
        B, args.out.replace('/', os.sep))
    write_all(out, neg, blind,
              datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    print('清單 → %s' % out)


if __name__ == '__main__':
    main()
