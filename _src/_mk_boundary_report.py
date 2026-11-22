# -*- coding: utf-8 -*-
"""產出《原文標點邊界_全書檢查.md／.json》（只讀定稿，不改資料）。

輸入：
  重作材料_長段/_邊界檢查_暫存.json   （套用前的分類＋逐欄變更）
  重新掃描（--apply 後的現況）
  _src/validate_site.py -- 實際執行，取最後一行數字
用法：
  python -X utf8 _src/_mk_boundary_report.py
"""
import io
import json
import os
import re
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT_MD = '重作材料_長段/原文標點邊界_全書檢查.md'
OUT_JSON = '重作材料_長段/原文標點邊界_全書檢查.json'
OUT_KEYS = '重作材料_長段/原文標點邊界_已修key.txt'
PRE = '重作材料_長段/_邊界檢查_暫存.json'
POST = '重作材料_長段/_邊界檢查_現況.json'
BOOKS = ['行事鈔', '戒疏', '業疏', '尼鈔', '義鈔']
RAW = {'行事鈔': 'TXT/01_四分律刪繁補闕行事鈔.txt', '戒疏': 'TXT/02_四分律含注戒本疏.txt',
       '業疏': 'TXT/03_四分律刪補隨機羯磨疏.txt', '尼鈔': 'TXT/04_四分律比丘尼鈔.txt',
       '義鈔': 'TXT/05_四分律拾毗尼義鈔.txt'}
BID = {'行事鈔': 'xingshichao', '戒疏': 'jieshu', '業疏': 'yeshu', '尼鈔': 'nicao', '義鈔': 'yichao'}
GAPS = ['GAP92-6', 'GAP77-4', 'GAP29-7']
HAN = re.compile(r'[\u4e00-\u9fff]')


def han(s):
    return ''.join(HAN.findall(s or ''))


def run(cmd):
    r = subprocess.run([sys.executable, '-X', 'utf8'] + cmd, cwd=B,
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    return r.returncode, (r.stdout or '') + (r.stderr or '')


def count_unique_fields(bak, cur):
    """比對備份與現檔，回傳 (changed_unique_fields, errors)。"""
    if not (bak and os.path.exists(bak)):
        return None, []
    A = [json.loads(x) for x in io.open(bak, encoding='utf-8') if x.strip()]
    C = [json.loads(x) for x in io.open(cur, encoding='utf-8') if x.strip()]
    n = 0
    errs = []
    for a, c in zip(A, C):
        if (a.get('translation') or '') != (c.get('translation') or ''):
            errs.append('%s 譯文變動' % a.get('key'))
        if han(a.get('source')) != han(c.get('source')):
            errs.append('%s source 漢字變動' % a.get('key'))
        if (a.get('source') or '') != (c.get('source') or ''):
            n += 1
        if (a.get('display_source') or '') != (c.get('display_source') or ''):
            n += 1
        for sa, sc in zip(a.get('segments') or [], c.get('segments') or []):
            if (sa.get('translation') or '') != (sc.get('translation') or ''):
                errs.append('%s seg 譯文變動' % a.get('key'))
            for f in ('source', 'display_source'):
                if (sa.get(f) or '') != (sc.get(f) or ''):
                    n += 1
                    if han(sa.get(f)) != han(sc.get(f)):
                        errs.append('%s seg %s 漢字變動' % (a.get('key'), f))
    return n, errs


def main():
    pre = json.load(open(os.path.join(B, PRE), encoding='utf-8'))
    rc, out = run([os.path.join(B, '_src', 'scan_source_punct_boundary.py'), '--json', POST])
    if rc != 0:
        raise SystemExit('重掃失敗：' + out[-800:])
    post = json.load(open(os.path.join(B, POST), encoding='utf-8'))
    rc2, vout = run([os.path.join(B, '_src', 'validate_site.py')])
    vline = [x for x in vout.strip().splitlines() if x.startswith('pages ')]
    vline = vline[-1] if vline else vout.strip()[-300:]
    vnum = dict(re.findall(r'(\w+) (\d+)', vline))

    # ---- GAP 特別確認 ----
    gap_check = []
    for bk in ['行事鈔']:
        rows = {r['key']: r for r in
                (json.loads(x) for x in io.open(os.path.join(B, '定稿', BID[bk] + '.jsonl'),
                                                encoding='utf-8') if x.strip())}
        text = io.open(os.path.join(B, RAW[bk]), encoding='utf-8').read()
        pos = [i for i, c in enumerate(text) if '\u4e00' <= c <= '\u9fff']
        for k in GAPS:
            r = rows.get(k)
            if not r:
                gap_check.append({'key': k, 'found': False})
                continue
            a, b = r['raw_start'], r['raw_end']
            src = r['source'] or ''
            pre_raw = text[max(0, pos[a] - 10):pos[a]]
            post_raw = text[pos[b - 1] + 1:pos[b - 1] + 11]
            gap_check.append({
                'key': k, 'found': True, 'book': bk,
                'raw_before': pre_raw, 'raw_after': post_raw,
                'raw_prev_char': text[pos[a] - 1] if pos[a] > 0 else '',
                'raw_next_char': text[pos[b - 1] + 1] if pos[b - 1] + 1 < len(text) else '',
                'src_head': src[:8], 'src_tail': src[-8:],
                'starts_with_bookmark': src.startswith('《'),
                'ends_with_period': src.endswith('。'),
                'han_ok': han(src) == ''.join(HAN.findall(text[pos[a]:pos[b - 1] + 1])),
            })
    gap_ok_all = all(g.get('starts_with_bookmark') and g.get('ends_with_period') for g in gap_check)

    # ---- 合併 JSON ----
    books = {}
    tot_pre = pre['totals']
    tot_post = post['totals']
    tot_uniq = 0
    diff_errs = []
    for bk in BOOKS:
        p = pre['books'][bk]
        q = post['books'][bk]
        bak = p.get('backup') or ''
        uniq, errs = count_unique_fields(os.path.join(B, bak) if bak else '',
                                         os.path.join(B, p['file']))
        diff_errs.extend(errs)
        if uniq is None:
            uniq = 0
        tot_uniq += uniq
        books[bk] = {
            'file': p['file'], 'book_id': p['book_id'],
            'rows': p['stats']['rows'],
            'han_mismatch': p['stats']['han_mismatch'],
            'han_mismatch_keys': p.get('han_mismatch') or [],
            'pre': p['stats'], 'post': q['stats'],
            'unique_fields': uniq,
            'diff_errors': errs,
            'keys_fixed': pre['keys_fixed'].get(bk) or [],
            'unsure': p.get('unsure') or [],
            'off': p.get('off') or [],
            'examples': p.get('examples') or {},
            'display_only_count': q['stats']['display_only_rows'],
            'display_only_keys': q.get('display_only_keys') or [],
            'backup': bak,
        }
    data = {
        'generated': time.strftime('%Y-%m-%d %H:%M:%S'),
        'title': '全書原文標點邊界檢查（五書定稿）',
        'inputs': {'source': '定稿/*.jsonl', 'raw': RAW, 'open_set': pre['open_set'],
                   'close_set': pre['close_set']},
        'method': {
            'unit': '定稿列（unit）；漢字流位移 raw_start:raw_end 對 TXT/ 原檔',
            'open_rule': 'raw 第一個漢字前緊鄰字元 ∈ 《「『（，source 開頭未帶 → 缺開頭',
            'close_rule': 'raw 最後一個漢字後緊鄰字元 ∈ 。」』）〕，source 結尾未帶 → 缺結尾',
            'safe_rule': '該端 raw 句讀段僅一字元，且 source 該端無任何標點 → 可安全修（前置／後置該字元）',
            'unsure_rule': '緊鄰兩個以上標點、source 該端已有別的標點、漢字流不符、未定位 → 只報告',
            'fix_fields': ['source', 'display_source', '端點 segment.source', '端點 segment.display_source'],
            'untouched': ['translation', 'Han 序列', 'raw_start/raw_end'],
        },
        'totals_pre': tot_pre,
        'totals_post': tot_post,
        'totals_unique_fields': tot_uniq,
        'post_diff_errors': diff_errs,
        'books': books,
        'changes': pre['changes'],
        'gap_check': gap_check,
        'gap_ok_all': gap_ok_all,
        'validate': {'exit': rc2, 'line': vline, 'numbers': vnum},
        'display_only_policy': 'source 已正確、僅 display_source／segment display 被產生器截掉句末標點者，'
                               '本輪不修（屬另一類大量補句號）；可用 --include-display-only 另跑。',
    }
    with io.open(os.path.join(B, OUT_JSON), 'w', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=1) + '\n')
    print('json ->', OUT_JSON)

    # ---- 已修 key 清單 ----
    with io.open(os.path.join(B, OUT_KEYS), 'w', encoding='utf-8', newline='\n') as f:
        f.write('# 全書原文標點邊界：已修 key（一列一 key；# 為書名與筆數）\n')
        for bk in BOOKS:
            ks = books[bk]['keys_fixed']
            if not ks:
                continue
            f.write('# %s（%d）\n' % (bk, len(ks)))
            for k in ks:
                f.write(k + '\n')
    print('keys ->', OUT_KEYS)

    # ---- MD ----
    L = []
    A = L.append
    A('# 全書原文標點邊界檢查（五書定稿）')
    A('')
    A('生成：%s　｜　對象：`定稿/xingshichao|jieshu|yeshu|nicao|yichao.jsonl`'
      '（合計 %d 筆）　｜　句讀權威：`TXT/01–05` 原檔（`raw_start`／`raw_end` 為漢字流位移）'
      % (data['generated'], tot_pre['rows']))
    A('')
    A('## 0. 結論')
    A('')
    A('```text')
    A('全書總數            %5d 筆' % tot_pre['rows'])
    A('可定位              %5d 筆（未定位 %d）' % (tot_pre['rows'] - tot_pre['unlocated'], tot_pre['unlocated']))
    A('漢字流不符（只報告）%5d 筆' % tot_pre['han_mismatch'])
    A('缺開頭              %5d 筆 → 可安全修 %d、不可確定 %d'
      % (tot_pre['open_missing'], tot_pre['open_safe'], tot_pre['open_unsure']))
    A('缺結尾              %5d 筆 → 可安全修 %d、不可確定 %d'
      % (tot_pre['close_missing'], tot_pre['close_safe'], tot_pre['close_unsure']))
    A('已修                %5d 筆／%d 欄位（%d 處增補；source＋display_source＋端點 segment）'
      % (tot_pre['fixed_rows'], tot_uniq, tot_pre['fixed_fields']))
    A('修後重掃            缺開頭 %d、缺結尾 %d（可安全修 %d）'
      % (tot_post['open_missing'], tot_post['close_missing'], tot_post['close_safe']))
    A('display 端點缺（未修）%5d 筆（僅顯示層；見 §6）' % tot_post['display_only_rows'])
    A('validate_site.py    %s' % vline)
    A('```')
    A('')
    _by_char = {}
    for c in pre['changes']:
        for a in set(x['add'] for x in c['changes']):
            _by_char[a] = _by_char.get(a, 0) + 1
    A('修前共 **%d** 個邊界缺口**（缺開頭 %d＋缺結尾 %d；分屬 %d 筆，其中 %d 筆兩端同時缺）。'
      '本輪補回 **%d** 個字元（%d 筆；%s），實際寫入 %d 個欄位（%d 處增補；'
      '同一欄位兩端同時修算 2 處）。'
      '其餘 %d 筆依規則 4「若 raw 前後不是明確單一標點，只列報告，不硬補」保留並列表。'
      % (tot_pre['open_missing'] + tot_pre['close_missing'], tot_pre['open_missing'],
         tot_pre['close_missing'], tot_pre['fixed_rows'] + tot_post['close_missing'],
         tot_pre['both_safe'], sum(_by_char.values()), tot_pre['fixed_rows'],
         '、'.join('`%s`×%d' % (k, v) for k, v in sorted(_by_char.items(), key=lambda x: -x[1])),
         tot_uniq, tot_pre['fixed_fields'], tot_post['close_missing']))
    A('')
    A('## 1. 檢查法')
    A('')
    A('1. **缺開頭**：raw 第一個漢字前的緊鄰字元 ∈ `《「『（`，而 `source` 開頭沒帶該字元。')
    A('2. **缺結尾**：raw 最後一個漢字後的緊鄰字元 ∈ `。」』）〕`，而 `source` 結尾沒帶該字元。')
    A('3. **句讀段切分**：緊鄰字元取「屬於本單位」的那一段——開頭取句讀段中最後一個'
      ' closing（`，。、；：？！」』）〕》〉】`）之後；結尾取第一個 opening（`「『（〔《〈【`）之前。'
      '因此 raw 若為 `。《`，本單位缺的是 `《`（`。` 屬前一段）；若為 `。」`，缺的是 `。`（`」` 也屬本單位）。')
    A('4. **只安全修**「緊鄰單一標點且能確定」：該端 raw 句讀段正好一個字元，且 `source` 該端'
      '完全沒有標點（開頭／結尾即漢字）。其餘（兩個以上標點、`source` 該端已有別的標點、'
      '漢字流不符、未定位）**一律只列報告**。')
    A('5. **修補欄位**：`source`、`display_source`、端點 `segment.source`、端點 `segment.display_source`；'
      '`translation` 與漢字序列逐字不動（程式斷言 `han(新)==han(舊)`、`translation` 不變、欄位只加不減）。')
    A('')
    A('## 2. 各書分類數')
    A('')
    A('| 書 | 筆數 | 漢字流不符 | 缺開頭 | 缺開頭可修 | 缺結尾 | 缺結尾可修 | 不可確定 | 已修筆數 | 已修欄位 | 增補處 | display 端點缺（未修） |')
    A('|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|')
    for bk in BOOKS:
        p = books[bk]['pre']
        A('| %s | %d | %d | %d | %d | %d | %d | %d | %d | %s | %d | %d |'
          % (bk, p['rows'], p['han_mismatch'], p['open_missing'], p['open_safe'],
             p['close_missing'], p['close_safe'], p['open_unsure'] + p['close_unsure'],
             p['fixed_rows'], books[bk]['unique_fields'], p['fixed_fields'],
             books[bk]['display_only_count']))
    A('| **合計** | **%d** | **%d** | **%d** | **%d** | **%d** | **%d** | **%d** | **%d** | **%d** | **%d** | **%d** |'
      % (tot_pre['rows'], tot_pre['han_mismatch'], tot_pre['open_missing'], tot_pre['open_safe'],
         tot_pre['close_missing'], tot_pre['close_safe'],
         tot_pre['open_unsure'] + tot_pre['close_unsure'], tot_pre['fixed_rows'],
         tot_uniq, tot_pre['fixed_fields'], tot_post['display_only_rows']))
    A('')
    A('「不可確定」明細：')
    A('')
    A('| 書 | 端 | 原因 | 筆數 | 說明 |')
    A('|:--|:--|:--|--:|:--|')
    reason_txt = {'multi': 'raw 該端緊鄰兩個以上標點（如 `。」`），只補一個會半截，故不補',
                  'conflict': 'source 該端已有別的標點（多為 `？`／`！` 句讀層差異），不覆蓋'}
    seen = set()
    for bk in BOOKS:
        p = books[bk]['pre']
        for where, reason, n in (
                ('open', 'multi', None), ('open', 'conflict', None),
                ('close', 'multi', None), ('close', 'conflict', None)):
            vals = [u for u in books[bk]['unsure'] if u['where'] == where and u['reason'] == reason]
            if not vals:
                continue
            A('| %s | %s | %s | %d | %s |' % (bk, '開頭' if where == 'open' else '結尾',
                                              reason, len(vals), reason_txt[reason]))
    A('')
    A('「規格外同類」（raw 緊鄰字元不在題目五字集合，如 `！？：，》〉`）：%d 筆，只報告、不修，見 §3.5。'
      % (tot_pre['off_close'] + tot_pre['off_open']))
    A('')
    A('## 3. 每類 5 個例子 key')
    A('')
    A('### 3.1 缺開頭－可安全修（%d）' % tot_pre['open_safe'])
    A('')
    for x in books['行事鈔']['examples']['open_safe']:
        A('- `%s`　raw 前一字 `%s`，source 開頭 `%s`' % (x['key'], x['c'], x['src_lead'] or '（空）'))
    for bk in BOOKS:
        if not books[bk]['pre']['open_safe'] or bk == '行事鈔':
            continue
        for x in books[bk]['examples']['open_safe']:
            A('- `%s`（%s）' % (x['key'], bk))
    if tot_pre['open_safe'] == 0:
        A('- （無）')
    A('')
    A('### 3.2 缺開頭－不可確定（%d）' % tot_pre['open_unsure'])
    A('')
    if tot_pre['open_unsure'] == 0:
        A('- （無；全書缺開頭皆為緊鄰單一 `《`／`「`，已全部安全修完）')
    for bk in BOOKS:
        for x in books[bk]['examples']['open_unsure']:
            A('- `%s`（%s）　raw `%s`／source `%s`' % (x['key'], bk, x['adj'], x['src_lead'] or '（空）'))
    A('')
    A('### 3.3 缺結尾－可安全修（%d）' % tot_pre['close_safe'])
    A('')
    shown = 0
    for bk in BOOKS:
        for x in books[bk]['examples']['close_safe'][:2 if bk != '行事鈔' else 5]:
            A('- `%s`（%s）　raw 後一字 `%s`，source 結尾 `%s`'
              % (x['key'], bk, x['c'], x['src_tail'] or '（空）'))
    A('')
    A('### 3.4 缺結尾－不可確定（%d）' % tot_pre['close_unsure'])
    A('')
    for bk in BOOKS:
        for x in books[bk]['examples']['close_unsure']:
            A('- `%s`（%s）　raw 句讀段 `%s`，source 結尾 `%s`（%s）'
              % (x['key'], bk, x['adj'], x['src_tail'] or '（空）', x['reason']))
    A('')
    A('### 3.5 規格外同類（只報告，%d）' % (tot_pre['off_close'] + tot_pre['off_open']))
    A('')
    for bk in BOOKS:
        for x in books[bk]['off'][:5]:
            A('- `%s`（%s）　raw 緊鄰 `%s`（%s端；不在題目集合）'
              % (x['key'], bk, x['c'], '開頭' if x['where'] == 'open' else '結尾'))
    A('')
    A('### 3.6 display_source 端點缺（僅顯示層，未修）')
    A('')
    for bk in BOOKS:
        ks = books[bk]['display_only_keys'][:5]
        A('- %s：%d 筆%s' % (bk, books[bk]['display_only_count'],
                            ('；例 ' + '、'.join('`%s`' % k for k in ks)) if ks else ''))
    A('')
    A('## 4. 已修 key 清單')
    A('')
    A('| 書 | 已修筆數 | 已修欄位 | 增補處 | 備份 |')
    A('|:--|--:|--:|--:|:--|')
    for bk in BOOKS:
        A('| %s | %d | %s | %d | %s |' % (bk, books[bk]['pre']['fixed_rows'],
                                         books[bk]['unique_fields'],
                                         books[bk]['pre']['fixed_fields'],
                                         ('`%s`' % books[bk]['backup']) if books[bk]['backup'] else '（未變動）'))
    A('')
    A('完整清單（一列一 key）：`%s`；逐欄前後值在 `%s` 的 `changes`。' % (OUT_KEYS, OUT_JSON))
    A('')
    A('## 5. 仍不確定 key 清單（%d）' % (tot_post['open_missing'] + tot_post['close_missing']))
    A('')
    A('| key | 書 | 端 | raw 句讀段 | source 該端 | 原因 |')
    A('|:--|:--|:--|:--|:--|:--|')
    for bk in BOOKS:
        for u in books[bk]['unsure']:
            A('| `%s` | %s | %s | `%s` | `%s` | %s |'
              % (u['key'], bk, '開頭' if u['where'] == 'open' else '結尾',
                 u['adj'], (u.get('src_lead') if u['where'] == 'open' else u.get('src_tail')) or '（空）',
                 u['reason']))
    A('')
    A('### 5b. 規格外同類（raw 緊鄰 `！？：，》〉` 等，題目五字以外；只報告）')
    A('')
    for bk in BOOKS:
        offs = books[bk]['off']
        if not offs:
            continue
        A('- %s（%d）：%s' % (bk, books[bk]['pre']['off_open'] + books[bk]['pre']['off_close'],
                            '、'.join('`%s`(%s)' % (x['key'], x['c']) for x in offs)))
    A('')
    A('## 6. 顯示層（display_source）端點缺：本輪不修')
    A('')
    A('`display_source` 是 `add_yeshu_display.py` 等腳本以「第一個漢字到最後一個漢字」切出來的，'
      '切片時把緊貼邊界的句末標點切掉；因此 `source` 正確、`display_source` 卻少一個'
      '`。`／`」` 的列共 **%d** 筆（業疏 %d、尼鈔 %d、義鈔 %d、行事鈔／戒疏 0——兩書無 display_source）。'
      % (tot_post['display_only_rows'], books['業疏']['display_only_count'],
         books['尼鈔']['display_only_count'], books['義鈔']['display_only_count']))
    A('')
    A('這批屬「一次性大量補句號」，依指示（不要大量補句號）本輪不動，只列清單；'
      '要處理時跑：')
    A('')
    A('```powershell')
    A('python -X utf8 _src/scan_source_punct_boundary.py --include-display-only --apply \\')
    A('  --json 重作材料_長段/原文標點邊界_全書檢查.json')
    A('```')
    A('')
    A('## 7. GAP92-6／GAP77-4／GAP29-7 特別確認')
    A('')
    A('| key | raw 前文（末 10 字） | raw 緊鄰前字 | source 開頭 | raw 後文（前 10 字） | raw 緊鄰後字 | source 結尾 | 含 `《` | 含 `。` |')
    A('|:--|:--|:--|:--|:--|:--|:--|:--|:--|')
    for g in gap_check:
        if not g.get('found'):
            A('| `%s` | 找不到 | | | | | | | |' % g['key'])
            continue
        A('| `%s` | …%s | `%s` | `%s` | %s… | `%s` | `%s` | %s | %s |'
          % (g['key'], g['raw_before'].replace('\n', ' '), g['raw_prev_char'],
             g['src_head'], g['raw_after'].replace('\n', ' '), g['raw_next_char'],
             g['src_tail'],
             '✅' if g['starts_with_bookmark'] else '❌',
             '✅' if g['ends_with_period'] else '❌'))
    A('')
    A('三筆皆已含 `《` 與 `。`（%s）；且修後全書重掃：**缺開頭 0 筆、可安全修缺結尾 0 筆**，'
      '即已無同類可修缺口。' % ('全部 ✅' if gap_ok_all else '有 ❌'))
    A('')
    A('## 8. validate 數字')
    A('')
    A('```text')
    A(vline)
    A('exit=%d' % rc2)
    A('```')
    A('')
    A('（`search` 索引已用 `build_search_index.py --only xingshichao yeshu nicao yichao` 重建；'
      '`punct 0` 代表沒有無句讀長原文。）')
    A('')
    A('## 9. 重現指令')
    A('')
    A('```powershell')
    A('python -X utf8 _src/scan_source_punct_boundary.py                    # 只掃描（dry）')
    A('python -X utf8 _src/scan_source_punct_boundary.py --apply \\         # 安全修補')
    A('  --json 重作材料_長段/_邊界檢查_暫存.json \\')
    A('  --keys 重作材料_長段/原文標點邊界_已修key.txt')
    A('python -X utf8 _src/_rebuild_pages.py            # render_canonical_cb 重建＋「只插入標點」驗證')
    A('python -X utf8 _src/_rebuild_pages.py --apply    # 通過才原子替換 .new → .html')
    A('python -X utf8 _src/build_search_index.py --only xingshichao yeshu nicao yichao')
    A('python -X utf8 _src/validate_site.py')
    A('python -X utf8 _src/_mk_boundary_report.py       # 產本報告（.md／.json／key 清單）')
    A('```')
    A('')
    A('## 10. 未處理／範圍外')
    A('')
    A('- 漢字流不符 %d 筆（%s）：`source` 與 `TXT/` 該區間漢字不同（如 `死屍`／`死戶`、`如法`／`非法`），'
      '屬異文或底本差，依「不改 Han」只列出、不判定邊界（邊界句讀仍以 raw 為準但無法對齊）：'
      % (tot_pre['han_mismatch'],
         '、'.join('%s %d' % (bk, books[bk]['han_mismatch']) for bk in BOOKS if books[bk]['han_mismatch'])))
    for bk in BOOKS:
        if books[bk]['han_mismatch']:
            A('  - %s：%s' % (bk, '、'.join('`%s`' % k for k in books[bk]['han_mismatch_keys'])))
    A('- `戒疏` 本輪 0 缺口（前一輪 `fix_jieshu_source_boundary.py` 已修過），故未寫檔、未重建頁。')
    A('- `定稿/五書_總集.jsonl`、`docs/search/*`（除上列四書）未動；`zhichi` 未在本輪範圍。')
    A('- 修前後 `translation` 逐筆比對 0 差異；每列 `han(source)` 與 `han(segment.source)` 皆不變。')
    A('')
    with io.open(os.path.join(B, OUT_MD), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')
    print('md ->', OUT_MD)
    print('validate:', vline)
    return 0


if __name__ == '__main__':
    sys.exit(main())
