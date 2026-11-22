# -*- coding: utf-8 -*-
"""定稿最終驗收：缺口盲翻合流門檻 ＋ 7 項最終驗收（只讀，不改資料）。

原有功能（缺口盲翻合流）：
  BLIND-*／GAP-* 必須先過 build_a2＋qc_scan 的同一組門檻，不得繞過寫進 定稿。

新增 --final：reaudit.txt 第 3/3 篇 §三「最終定稿重建與強制驗收」7 項：
  1. source == raw[raw_start:raw_end]              → 100%（資持記無可靠底本，標未驗）
  2. 未定位筆數                                     → 0
  3. 區間重疊筆數                                   → 0
  4. 空白譯文／缺欄                                 → 0
  5. 缺開頭標籤／背景標籤外洩                       → 0
  6. GAP*／BLIND-*／JE-*／YE-* 皆有再審／再修紀錄   → 100%（未跑批時標待跑）
  7. 非正文（卷題、目錄、校勘表）如實排除，不假補洞 → 清單核對（--strict 才算失敗）

用法：
  python -X utf8 _src/check_final_merge.py --book 尼鈔
  python -X utf8 _src/check_final_merge.py --book 尼鈔 --all
  python -X utf8 _src/check_final_merge.py --book 戒疏 --final
  python -X utf8 _src/check_final_merge.py --book 戒疏 --final --plan 測試/重譯/戒疏/_再審/_再審拆回_計畫.json
  python -X utf8 _src/check_final_merge.py --book 戒疏 --final --strict
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
LEAD_LAB = re.compile(r'^\s*【(%s)】' % '|'.join(LABELS + ('記序',)))
GAP_PREFIX = ('BLIND-', 'GAP')
JUNK = re.compile(r'---\s*START OF FILE|```\s*\n|【原文】|【待審譯文】|【前文背景|'
                  r'(?:local_search|web_search|web_fetch)\s*\(')
BG_TAGS = ('【前文背景', '【後文背景', '【所釋鈔文', '【待審譯文',
           '【分段核驗表】', '【必改硬傷】', '【本次待審')
# 非正文（卷題／目錄／校勘／異體字表）常用提示；不收「卷上／卷中」這種正文也會回指的詞
NONBODY_HINTS = ('目錄', '凡例', '科判', '校勘', '異體字', '大覺慈父', '九十單提法',
                 '百眾學法', '四分戒本》者', '甞聞毗尼藏', '原夫大雄', '疏卷第一')
RAW_FILES = {
    '業疏': 'TXT_句讀校定/yeshu.txt',
    '戒疏': 'TXT_句讀校定/jieshu.txt',
    '尼鈔': 'TXT_句讀校定/nicao.txt',
    '行事鈔': 'TXT_句讀校定/xingshichao.txt',
    '義鈔': 'TXT_句讀校定/yichao.txt',
    '資持記': '',   # 定稿 raw 位移與 TXT_句讀校定 不同制
}
_HAN = re.compile(r'[\u4e00-\u9fff]')


def han(s):
    return ''.join(_HAN.findall(s or ''))


def _rows(path):
    return [json.loads(x) for x in io.open(path, encoding='utf-8') if x.strip()]


def _parts(row):
    segs = [s for s in (row.get('segments') or [])
            if (s.get('source') or s.get('translation'))]
    if segs:
        return [{'lab': s.get('label') or row.get('label') or '',
                 'orig': s.get('source') or '',
                 'tr': s.get('translation') or ''} for s in segs]
    return [{'lab': row.get('label') or '',
             'orig': row.get('source') or '',
             'tr': row.get('translation') or ''}]


def _rel(p):
    try:
        return os.path.relpath(p, B)
    except ValueError:
        return p


# ---------------------------------------------------------------- 原有缺口合流檢查
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


# ---------------------------------------------------------------- 7 項最終驗收
def final_checks(book, plan_path='', revise_dir='', strict=False):
    bid = BOOKS[book]
    p = os.path.join(B, '定稿', bid + '.jsonl')
    if not os.path.exists(p):
        raise SystemExit('找不到定稿：' + p)
    rows = _rows(p)
    raw_h, raw_path = None, RAW_FILES.get(book, '')
    if raw_path:
        fp = os.path.join(B, raw_path.replace('/', os.sep))
        if os.path.exists(fp):
            raw_h = han(io.open(fp, encoding='utf-8').read())
    items = []

    # 1) source == raw[raw_start:raw_end]
    bad1, ok1 = [], 0
    for r in rows:
        a = int(r.get('raw_start', -1) or -1)
        b = int(r.get('raw_end', -1) or -1)
        if raw_h is None:
            continue
        if 0 <= a < b <= len(raw_h) and raw_h[a:b] == han(r.get('source')):
            ok1 += 1
        else:
            bad1.append((r.get('key') or '?', a, b))
    if raw_h is None:
        items.append(('source == raw', '未驗', 0, len(rows),
                      '無可靠底本（定稿位移與 TXT_句讀校定 不同制）'))
    else:
        items.append(('source == raw', 'OK' if not bad1 else 'FAIL',
                      ok1, len(rows),
                      '；'.join('%s(%s:%s)' % (k, a, b) for k, a, b in bad1[:8])))

    # 2) 未定位
    bad2 = [r.get('key') or '?' for r in rows
            if int(r.get('raw_start', -1) or -1) < 0
            or int(r.get('raw_end', -1) or -1) <= int(r.get('raw_start', -1) or -1)
            or (raw_h is not None and int(r.get('raw_end', -1) or -1) > len(raw_h))]
    items.append(('未定位', 'OK' if not bad2 else 'FAIL', len(rows) - len(bad2),
                  len(rows), '、'.join(str(x) for x in bad2[:10])))

    # 3) 區間重疊
    bad3 = []
    for vol in {r.get('vol') or '' for r in rows}:
        grp = sorted([r for r in rows if (r.get('vol') or '') == vol
                      and int(r.get('raw_start', -1) or -1) >= 0],
                     key=lambda r: int(r['raw_start']))
        for x, y in zip(grp, grp[1:]):
            if int(y['raw_start']) < int(x['raw_end']):
                bad3.append('%s∩%s' % (x.get('key'), y.get('key')))
    items.append(('區間重疊', 'OK' if not bad3 else 'FAIL',
                  len(rows) - len(bad3), len(rows), '、'.join(bad3[:10])))

    # 4) 空白譯文／缺欄
    bad4 = []
    for r in rows:
        parts = _parts(r)
        if not han(r.get('translation')):
            bad4.append('%s(空白)' % (r.get('key') or '?'))
            continue
        for x in parts:
            if han(x['orig']) and not han(x['tr']):
                bad4.append('%s(%s缺欄)' % (r.get('key') or '?', x['lab'] or '?'))
                break
    items.append(('空白譯文／缺欄', 'OK' if not bad4 else 'FAIL',
                  len(rows) - len(bad4), len(rows), '、'.join(bad4[:10])))

    # 5) 缺開頭標籤／背景外洩
    bad5 = []
    for r in rows:
        tr = r.get('translation') or ''
        if not LEAD_LAB.match(tr):
            bad5.append('%s(缺標籤)' % (r.get('key') or '?'))
            continue
        if any(t in tr for t in BG_TAGS):
            bad5.append('%s(背景外洩)' % (r.get('key') or '?'))
    items.append(('缺開頭標籤／背景外洩', 'OK' if not bad5 else 'FAIL',
                  len(rows) - len(bad5), len(rows), '、'.join(bad5[:10])))

    # 6) GAP／BLIND／JE／YE 再審紀錄
    gap_keys = [r.get('key') or '' for r in rows
                if re.search(r'GAP|BLIND|(?:^|[_-])JE-|(?:^|[_-])YE-', r.get('key') or '')]
    if not plan_path:
        for cand in ('測試/重譯/%s/_再審/_再審拆回_計畫.json' % book,):
            cp = os.path.join(B, cand.replace('/', os.sep))
            if os.path.exists(cp):
                plan_path = cp
                break
    audited, revised, plan_note = set(), set(), ''
    plan = None
    if plan_path:
        pp = plan_path if os.path.isabs(plan_path) else os.path.join(B, plan_path.replace('/', os.sep))
        if os.path.exists(pp):
            plan = json.load(io.open(pp, encoding='utf-8'))
            audited = set(plan.get('pass') or []) | set(plan.get('fix') or {})
            rd = (revise_dir or '測試/重譯/%s/_再審修訂' % book)
            rep = os.path.join(B, rd.replace('/', os.sep), '回覆')
            for k in (plan.get('fix') or {}):
                if os.path.exists(os.path.join(rep, k + '_回.txt')):
                    revised.add(k)
            plan_note = _rel(pp)
    if plan is None:
        items.append(('缺口段再審紀錄', '待跑', 0, len(gap_keys),
                      '找不到拆回計畫（未跑批）；GAP／BLIND／JE／YE 共 %d 段' % len(gap_keys)))
    else:
        miss_a = [k for k in gap_keys if k not in audited]
        miss_r = [k for k in gap_keys if k in (plan.get('fix') or {}) and k not in revised]
        ok6 = len(gap_keys) - len(miss_a) - len(miss_r)
        st = 'OK' if not miss_a and not miss_r else 'FAIL'
        items.append(('缺口段再審紀錄', st, ok6, len(gap_keys),
                      ('%s；' % plan_note)
                      + ('未再審 %d：%s；' % (len(miss_a), '、'.join(miss_a[:8])) if miss_a else '')
                      + ('未再修 %d：%s' % (len(miss_r), '、'.join(miss_r[:8])) if miss_r else '')))

    # 7) 非正文如實排除（只列清單，--strict 才算失敗）
    nb = []
    for r in rows:
        src = r.get('source') or ''
        if any(h in src for h in NONBODY_HINTS) and han(r.get('translation')):
            nb.append(r.get('key') or '?')
    items.append(('非正文如實排除', 'OK' if not nb else 'WARN',
                  len(rows) - len(nb), len(rows),
                  '疑非正文卻有譯文（前 10）：' + '、'.join(nb[:10]) if nb else ''))
    return items


def _print_final(book, items, strict):
    print('最終驗收（%s）｜7 項' % book)
    print('| # | 項目 | 結果 | 達成 | 備註 |')
    print('|--:|:--|:--|--:|:--|')
    hard_fail = False
    n_ok = 0
    for i, (name, st, ok, total, note) in enumerate(items, 1):
        mark = {'OK': '✅', 'FAIL': '❌', '未驗': '➖', '待跑': '⏳', 'WARN': '⚠'}.get(st, st)
        if st == 'OK':
            n_ok += 1
        print('| %d | %s | %s %s | %d／%d | %s |'
              % (i, name, mark, st, ok, total, (note or '').replace('\n', ' ')[:180]))
        if st == 'FAIL' or (strict and st in ('未驗', '待跑', 'WARN')):
            hard_fail = True
    print('達標 %d／%d（--strict 才把未驗／待跑／WARN 計為失敗）' % (n_ok, len(items)))
    return hard_fail


def main():
    ap = argparse.ArgumentParser(
        description='定稿最終驗收：缺口合流檢查 ＋ 7 項最終驗收（只讀）')
    ap.add_argument('--book', required=True, choices=sorted(BOOKS))
    ap.add_argument('--all', action='store_true', help='連非缺口段一併檢查（只報不擋）')
    ap.add_argument('--reply-dir', default='')
    ap.add_argument('--final', action='store_true', help='執行 7 項最終驗收')
    ap.add_argument('--plan', default='', help='再審拆回計畫（預設自動找 _再審/）')
    ap.add_argument('--revise-dir', default='', help='再修目錄（預設 測試/重譯/<book>/_再審修訂）')
    ap.add_argument('--strict', action='store_true',
                    help='未驗／待跑／WARN 也算失敗（rc=1）')
    args = ap.parse_args()

    hard, n, warn = check_rows(args.book, args.all)
    if args.reply_dir:
        for x in check_replies(args.book, args.reply_dir):
            hard.append('回覆：' + x)
    print('缺口合流檢查 %d 段｜硬傷 %d｜提醒 %d' % (n, len(hard), len(warn)))
    for x in hard[:40]:
        print('  ✗', x)
    for x in warn[:20]:
        print('  ⚠', x)

    final_fail = False
    if args.final:
        items = final_checks(args.book, args.plan, args.revise_dir, args.strict)
        print('')
        final_fail = _print_final(args.book, items, args.strict)

    if hard:
        print('缺口盲翻未通過合流門檻，不得寫入定稿')
        raise SystemExit(1)
    if final_fail:
        print('7 項最終驗收未達標')
        raise SystemExit(1)
    print('缺口合流檢查通過' + ('；7 項最終驗收已跑（見上表）' if args.final else '') )


if __name__ == '__main__':
    main()
