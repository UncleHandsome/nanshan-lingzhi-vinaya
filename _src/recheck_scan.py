# -*- coding: utf-8 -*-
"""確定性前置掃描（recheck_scan）：掃 定稿/*.jsonl，貼 risk_flags，只輸出報告、不改資料。

規格（reaudit.txt 第 1/3 篇 §三、第 3/3 篇 §二）：
  1. 譯文空白／缺欄／source 開頭 】」、／結尾缺句末
  2. 缺開頭白名單標籤
  3. 背景外洩（【前文背景】等材料標籤）
  4. GAP／BLIND／JE-／YE- 缺口段（必再審）
  5. 第三人稱撰者旁白（源無道宣／元照／南山，譯文卻出現）
  6. 白話引號內殘留 BAD_VAR（只豁免與 src 原字一致之引詞）
  7. 譯文〔…〕多於原文
  8. 結尾冒號、「的等。」、「？等等。」
  9. 膨脹 >1.9／縮水 <0.5、孤立單層『』
 10. 雙欄總數詞／無標點多「云言問答曰」／破折號長插注／序跋高風險
 11. FALSE_FRIEND_HIT（30+ 高危假朋友）＋ BOOK_TERM_HIT（各書具體詞旗標）
     —— 兩者只作排序／報告，不表示必審；未命中不得當跳過再審的依據

用法：
  python -X utf8 _src/recheck_scan.py
  python -X utf8 _src/recheck_scan.py --book 尼鈔
  python -X utf8 _src/recheck_scan.py --book 戒疏 --json 重作材料_長段/_掃描/戒疏.json
  python -X utf8 _src/recheck_scan.py --strict          # 有致命旗標即 rc=1
  python -X utf8 _src/recheck_scan.py --out 重作材料_長段/再審前置掃描.md

本檔只讀取 定稿/*.jsonl；不寫任何 定稿／docs／材料檔。
"""
import argparse
import datetime
import io
import json
import os
import re
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'

BOOKS = {
    '業疏': 'yeshu',
    '戒疏': 'jieshu',
    '尼鈔': 'nicao',
    '行事鈔': 'xingshichao',
    '義鈔': 'yichao',
    '資持記': 'zhichi',
}

LABELS = ('疏文', '記文', '鈔文', '律文', '註文', '序文', '記序')
LEAD_LAB = re.compile(r'^\s*【(%s)】' % '|'.join(LABELS))
SRC_HEAD_BAD = re.compile(r'^[】」』、，,。；;：:）)\]】]')
SRC_TAIL_OK = '。！？…」』）〕】〉》”'
BAD_VAR = ('却', '鉢', '厨', '徧', '牀', '説', '衆')
BG_TAGS = ('【前文背景', '【後文背景', '【所釋鈔文', '【所釋疏文', '【待審譯文',
           '【本次待審', '【裁決檢索摘錄', '【原典夾注', '【原典雙行夾注',
           '【資持記相關釋文', '【義鈔輔要記', '【分段核驗表】', '【必改硬傷】',
           '【逐句簡核】', '〔定稿殘留')
TP_WORDS = ('道宣', '元照', '南山律師', '南山', '律祖')
GAP_RE = re.compile(r'GAP|BLIND|(?:^|[_-])JE-|(?:^|[_-])YE-')
DIALOG_RE = re.compile(r'[云言問答曰]')
PUNCT = '，。；：！？、'
TOTAL_WORDS = ('八事', '五事', '四門', '十門', '二者', '兩者', '九事', '六事', '三事', '七事')
PREFACE_RE = re.compile(r'^\s*(?:序|敘|叙|原夫|蓋聞|竊以|謹序|題辭)|卷首|會本|江戶')

# ---- 高危假朋友（全書通用；只作 0 成本旗標，不進提示詞） ----
FALSE_FRIEND = (
    '中國', '人語', '通解', '餘論', '入宗', '一期', '餘食法', '八遮', '通局',
    '下手疏', '口說', '投竄', '眼暗', '來者', '何法', '長者', '須用物', '惡捉',
    '上中下', '背別', '供須', '已將久', '為妨', '制意', '中氣', '二者',
    '疏人', '造逆', '教通', '克定', '有通有局',
)
# ---- 各書抽樣已證實的具體詞（旗標用；提示詞不得引用） ----
# 只作「排序／報告／人工優先序」：命中不表示必審，未命中更不得當作跳過再審的依據；
# 再審範圍一律以 定稿 全量為準（見 AGENTS 7A 與 流程_再審 §7）。
BOOK_TERMS = {
    '尼鈔': ('刮刀', '波羅夷', '房舍田園', '招提', '十三步', '體毛', '髮長', '僧物', '式叉摩那'),
    '行事鈔': ('不作餘食法', '八遮', '有通有局', '下手疏', '何法持三衣', '投竄', '教通餘論', '克定一期'),
    '義鈔': ('執情三品', '背別', '目連', '疏人', '三家', '上中下', '婆沙論', '本自無過'),
    '業疏': ('八事', '九事', '得在浮沈', '隱顯互見', '初文隨相', '非受體', '今已將久'),
    '戒疏': ('六七百年', '江戶', '如上所引', '罪相等故', '中氣', '二者', '記序'),
    '資持記': ('所釋鈔文', '某下', '此下', '牒字', '一期'),
}

# 致命（資料層確定壞掉；缺開頭標籤屬各書慣例問題，列風險旗標不列致命）
FATAL = {'EMPTY_TR', 'MISSING_FIELD', 'DUAL_MISSING_COL', 'SRC_HEAD_CLOSE',
         'SRC_TAIL_NO_END', 'BG_LEAK', 'BAD_VAR_QUOTE',
         'BRACKET_OVERFLOW', 'TAIL_COLON', 'DE_DENG', 'Q_WENDENG'}
SOURCE_STRICT = {'MISSING_FIELD', 'SRC_HEAD_CLOSE', 'SRC_TAIL_NO_END'}
FLAG_ORDER = (
    'EMPTY_TR', 'MISSING_FIELD', 'DUAL_MISSING_COL', 'SRC_HEAD_CLOSE',
    'SRC_TAIL_NO_END', 'NO_LEAD_LABEL', 'BG_LEAK', 'GAP_SEG', 'THIRD_PERSON',
    'BAD_VAR_QUOTE', 'BAD_VAR_OUTSIDE', 'LABEL_203_REVIEW',
    'BRACKET_OVERFLOW', 'TAIL_COLON', 'DE_DENG', 'Q_WENDENG',
    'INFLATE', 'SHRINK', 'LONE_CORNER', 'DUAL_TOTAL', 'NO_PUNCT_DIALOG',
    'DASH_NOTE', 'PREFACE_RISK', 'FALSE_FRIEND_HIT', 'BOOK_TERM_HIT',
)
_HAN = re.compile(r'[\u4e00-\u9fff]')


def han(s):
    return ''.join(_HAN.findall(s or ''))


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


def _ratio_plain(tr):
    """漢字數（排除夾注／校勘括號內容，避免夾注白話重複計入膨脹率）。"""
    t = re.sub(r'（[^）]*）|\([^)]*\)|〔[^〕]*〕', '', tr or '')
    return len(han(t))


def _quote_bad(tr, src):
    """白話引號內殘留 BAD_VAR；src 同字者視為被訓釋原詞，豁免。"""
    for q in re.findall(r'[「『]([^」』]{1,})[」』]', tr or ''):
        for ch in BAD_VAR:
            if ch in q and ch not in (src or ''):
                return ch
    return ''


def scan_row(book, row, raw_h=None, inflate_thr=1.9, shrink_thr=0.5):
    """回傳 {'flags': [...], 'detail': {...}}。inflate_thr 由 scan_book 依全書中位數調整。"""
    flags, detail = [], {}

    def add(f, **kw):
        if f not in flags:
            flags.append(f)
        if kw:
            detail.setdefault(f, {}).update(kw)

    key = str(row.get('key') or '')
    tr = row.get('translation')
    src = row.get('source') or ''
    parts = _parts(row)

    if 'translation' not in row or tr is None:
        add('MISSING_FIELD', field='translation')
        tr = ''
    if not isinstance(tr, str):
        add('MISSING_FIELD', field='translation(type)')
        tr = ''
    if not src:
        add('MISSING_FIELD', field='source')

    sh = len(han(src))
    oh = _ratio_plain(tr)
    if not han(tr):
        add('EMPTY_TR', han=0)
    _by_lab = {}
    for p in parts:
        if p['lab']:
            _by_lab.setdefault(p['lab'], []).append(p)
    if len(_by_lab) > 1:
        _empty = [lab for lab, ps in _by_lab.items()
                  if ps and all(not han(x['tr']) for x in ps)]
        if _empty:
            add('DUAL_MISSING_COL', empty=_empty)

    _s = src.strip()
    if _s and SRC_HEAD_BAD.match(_s):
        add('SRC_HEAD_CLOSE', head=_s[:12])
    # 短科判標目（無句讀）不強求句末標點，避免整本書的科名洗版
    if _s and _s[-1] not in SRC_TAIL_OK and (sh >= 20 or any(c in _s for c in '。，；')):
        add('SRC_TAIL_NO_END', tail=_s[-12:])

    if tr and not LEAD_LAB.match(tr):
        add('NO_LEAD_LABEL', head=tr.strip()[:16])
    leaked = [t for t in BG_TAGS if t in (tr or '')]
    if leaked:
        add('BG_LEAK', tags=leaked)

    if GAP_RE.search(key):
        add('GAP_SEG', key=key)

    if tr and any(w in tr for w in TP_WORDS) and not any(w in src for w in ('道宣', '元照', '南山', '律祖')):
        add('THIRD_PERSON', words=[w for w in TP_WORDS if w in tr][:3])

    _bv = _quote_bad(tr, src)
    if _bv:
        add('BAD_VAR_QUOTE', char=_bv)
    # 引號外異體字（不豁免 src 同字；只報告）
    _noq = re.sub(r'[「『][^」』]*[」』]', '', tr or '')
    _bv_out = [c for c in BAD_VAR if c in _noq]
    if _bv_out:
        add('BAD_VAR_OUTSIDE', chars=_bv_out)

    # 義鈔 203 標籤／display 篇題疑點：只報告，不改資料
    if book == '義鈔' and key == '203':
        labs = [p.get('lab') for p in parts if p.get('lab')]
        disp = row.get('display_source') or ''
        if labs and set(labs) == {'鈔文'} and re.search(r'卷[一二三四]|篇|章', disp[:120]):
            add('LABEL_203_REVIEW', labs=labs, display=disp[:80])

    if (tr or '').count('〔') > src.count('〔'):
        add('BRACKET_OVERFLOW', out=tr.count('〔'), src=src.count('〔'))

    _t = (tr or '').rstrip()
    if _t.endswith(('：', ':')):
        add('TAIL_COLON', tail=_t[-10:])
    if '的等。' in (tr or ''):
        add('DE_DENG')
    if re.search(r'[？?]等等。', tr or ''):
        add('Q_WENDENG')

    if sh >= 10 and oh > sh * inflate_thr:
        add('INFLATE', src_han=sh, out_han=oh, ratio=round(oh / sh, 2),
            threshold=inflate_thr)
    if sh >= 10 and oh < sh * shrink_thr:
        add('SHRINK', src_han=sh, out_han=oh, ratio=round((oh / sh) if sh else 0, 2),
            threshold=shrink_thr)
    if tr and '「' not in tr and ('『' in tr or '』' in tr):
        add('LONE_CORNER')

    if len(parts) > 1:
        _hit = [w for w in TOTAL_WORDS if w in tr or w in src]
        if _hit:
            add('DUAL_TOTAL', words=_hit[:4])

    _punct = sum(src.count(ch) for ch in PUNCT)
    if sh >= 60 and _punct <= 1 and len(DIALOG_RE.findall(src)) >= 2:
        add('NO_PUNCT_DIALOG', punct=_punct, dialog=len(DIALOG_RE.findall(src)))

    if '——' in (tr or ''):
        add('DASH_NOTE')
    if '序文' == (row.get('label') or '') or PREFACE_RE.search(key + ' ' + src[:60]):
        add('PREFACE_RISK')

    ff = [w for w in FALSE_FRIEND if w in src]
    if ff:
        add('FALSE_FRIEND_HIT', words=ff[:8])
    bt = [w for w in BOOK_TERMS.get(book, ()) if w in src]
    if bt:
        add('BOOK_TERM_HIT', words=bt[:8])

    return {'book': book, 'key': key,
            'vol': row.get('vol') or '', 'chunk': row.get('chunk') or '',
            'src_han': sh, 'tr_han': oh, 'flags': flags, 'detail': detail}


def scan_book(book, jsonl=None):
    bid = jsonl or BOOKS[book]
    p = os.path.join(B, '定稿', bid + '.jsonl')
    if not os.path.exists(p):
        raise SystemExit('找不到定稿：%s' % p)
    raws, bad = [], []
    with io.open(p, encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                raws.append(json.loads(line))
            except Exception as e:
                bad.append({'book': book, 'key': '?', 'vol': '', 'chunk': '',
                            'src_han': 0, 'tr_han': 0,
                            'flags': ['MISSING_FIELD'],
                            'detail': {'MISSING_FIELD': {'error': str(e)[:80]}}})
    # 各書底本長度／譯文長度比例差異大（業疏中位數約 2.1），
    # 絕對 1.9 會把正常段全打成膨脹；以「全書中位數 ×1.25，且不低於 1.9」為門檻。
    _rs = []
    for r in raws:
        sh = len(han(r.get('source')))
        if sh >= 10:
            _rs.append(_ratio_plain(r.get('translation')) / sh)
    _rs.sort()
    median = _rs[len(_rs) // 2] if _rs else 0.0
    inflate_thr = max(1.9, round(median * 1.25, 2)) if median else 1.9
    rows = [scan_row(book, r, inflate_thr=inflate_thr) for r in raws]
    rows.extend(bad)
    return {'book': book, 'file': '定稿/%s.jsonl' % bid, 'rows': len(rows),
            'median_ratio': round(median, 2), 'inflate_thr': inflate_thr,
            'items': rows}


def summarize(result):
    items = result['items']
    counts = {}
    keys_by = {}
    n_fatal = 0
    for it in items:
        _fatal = [f for f in it['flags'] if f in FATAL]
        if _fatal:
            n_fatal += 1
        for f in it['flags']:
            counts[f] = counts.get(f, 0) + 1
            keys_by.setdefault(f, []).append(it['key'])
    return {'book': result['book'], 'file': result['file'], 'rows': result['rows'],
            'flagged': sum(1 for it in items if it['flags']),
            'fatal_rows': n_fatal,
            'median_ratio': result.get('median_ratio'),
            'inflate_thr': result.get('inflate_thr'),
            'counts': {f: counts[f] for f in FLAG_ORDER if f in counts},
            'keys': {f: keys_by[f] for f in FLAG_ORDER if f in keys_by}}


def _fmt_summary(s):
    head = '%-6s %6s 筆｜有旗標 %5s｜致命 %4s｜比例中位 %s（膨脹門檻 %s）' % (
        s['book'], s['rows'], s['flagged'], s['fatal_rows'],
        s.get('median_ratio'), s.get('inflate_thr'))
    bits = []
    for f, c in s['counts'].items():
        bits.append('%s %d' % (f, c))
    return head + ('\n        ' + '；'.join(bits) if bits else '')


def write_report(path, all_res, sums, generated):
    L = ['# 再審前置確定性掃描（recheck_scan）', '',
         '- 產生時間：%s' % generated,
         '- 來源：`定稿/*.jsonl`（只讀；未改任何資料）',
         '- 用途：0 成本風險旗標；`FALSE_FRIEND_HIT`／`BOOK_TERM_HIT` 只在本程式內，不進提示詞。',
         '']
    tot_rows = sum(s['rows'] for s in sums)
    tot_flag = sum(s['flagged'] for s in sums)
    tot_fatal = sum(s['fatal_rows'] for s in sums)
    L += ['## 總覽', '',
          '| 書 | 筆數 | 有旗標 | 致命 | 比例中位 | 膨脹門檻 | 旗標分佈 |',
          '|:--|--:|--:|--:|--:|--:|:--|']
    for s in sums:
        L.append('| %s | %s | %s | %s | %s | %s | %s |'
                 % (s['book'], s['rows'], s['flagged'], s['fatal_rows'],
                    s.get('median_ratio'), s.get('inflate_thr'),
                    '；'.join('%s %d' % (f, c) for f, c in s['counts'].items()) or '—'))
    L += ['| **合計** | **%d** | **%d** | **%d** | — | — | — |' % (tot_rows, tot_flag, tot_fatal), '',
          '> 譯文／原文漢字比的中位數各書不同（業疏約 2.1）；`INFLATE` 門檻取'
          '「max(1.9, 全書中位數×1.25)」，避免正常語體擴寫被整本書誤標。', '']

    L += ['## 致命旗標明細（每項最多 20 鍵）', '']
    any_fatal = False
    for s in sums:
        for f in FLAG_ORDER:
            if f in s['keys'] and f in FATAL:
                any_fatal = True
                L.append('- **%s %s**（%d）：%s'
                         % (s['book'], f, len(s['keys'][f]),
                            '、'.join(s['keys'][f][:20])))
    if not any_fatal:
        L.append('- 無。')
    L += ['', '## 風險旗標明細（非致命，供排優先序）', '']
    for s in sums:
        soft = [(f, s['keys'][f]) for f in FLAG_ORDER
                if f in s['keys'] and f not in FATAL]
        if not soft:
            continue
        L.append('### %s' % s['book'])
        for f, ks in soft:
            L.append('- %s（%d）：%s' % (f, len(ks), '、'.join(ks[:15])))
        L.append('')
    L += ['## 旗標定義', '',
          '| 旗標 | 意義 |', '|:--|:--|',
          '| EMPTY_TR | 整筆譯文無漢字 |',
          '| MISSING_FIELD | 缺 translation／source 欄或型別錯 |',
          '| DUAL_MISSING_COL | 雙欄段有一欄空白 |',
          '| SRC_HEAD_CLOSE | source 開頭為 】」、，。；： 等（邊界截斷） |',
          '| SRC_TAIL_NO_END | source 結尾非句末標點 |',
          '| BAD_VAR_OUTSIDE | 引號外殘留却／鉢／厨／徧／牀／説／衆（只報告） |',
          '| LABEL_203_REVIEW | 義鈔 203 標籤或 display 篇題疑點（只報告） |',
          '| NO_LEAD_LABEL | 譯文開頭缺白名單段別標籤 |',
          '| BG_LEAK | 譯文殘留材料背景／清單標籤 |',
          '| GAP_SEG | key 屬 GAP／BLIND／JE-／YE- 缺口段（必再審） |',
          '| THIRD_PERSON | 源無撰者名而譯文出現第三人稱旁白 |',
          '| BAD_VAR_QUOTE | 引號內殘留却／鉢／厨／徧／牀／説／衆（src 同字豁免） |',
          '| BRACKET_OVERFLOW | 譯文〔…〕多於原文 |',
          '| TAIL_COLON | 譯文結尾懸空冒號 |',
          '| DE_DENG / Q_WENDENG | 出現「的等。」／「？等等。」 |',
          '| INFLATE / SHRINK | 譯文漢字 >門檻／<0.5× 原文（夾注不計；門檻見總覽） |',
          '| LONE_CORNER | 無「」卻有孤立『』 |',
          '| DUAL_TOTAL | 雙欄段含總數詞／二者／兩者 |',
          '| NO_PUNCT_DIALOG | 原文無標點且 ≥2 次云言問答曰 |',
          '| DASH_NOTE | 含破折號長插注 —— |',
          '| PREFACE_RISK | 卷首／序跋／駢文高風險 |',
          '| FALSE_FRIEND_HIT | 命中全書通用高危假朋友（只在本程式） |',
          '| BOOK_TERM_HIT | 命中該書抽樣已證實具體詞；**只作排序／報告，不作跳過再審依據** |',
          '']
    d = os.path.dirname(os.path.abspath(path))
    if d:
        os.makedirs(d, exist_ok=True)
    io.open(path, 'w', encoding='utf-8').write('\n'.join(L))


def main():
    ap = argparse.ArgumentParser(
        description='確定性前置掃描：掃 定稿/*.jsonl 貼 risk_flags（只讀，不改資料）')
    ap.add_argument('--book', default='全部', choices=list(BOOKS) + ['全部'],
                    help='書別（預設全部六書）')
    ap.add_argument('--json', nargs='?', const='-', default=None,
                    metavar='PATH', help='輸出 JSON（不給 PATH 則印到 stdout）')
    ap.add_argument('--out', default='', help='輸出 Markdown 報告（選填）')
    ap.add_argument('--strict', action='store_true',
                    help='相容舊參數：等同 --strict-all')
    ap.add_argument('--strict-source', action='store_true',
                    help='只檢查 source 邊界旗標；有則 rc=1')
    ap.add_argument('--strict-all', action='store_true',
                    help='所有致命旗標（含譯文）有則 rc=1')
    ap.add_argument('--limit', type=int, default=0,
                    help='只掃前 N 筆（除錯用；0＝全部）')
    args = ap.parse_args()

    books = list(BOOKS) if args.book == '全部' else [args.book]
    results, sums = [], []
    for bk in books:
        r = scan_book(bk)
        if args.limit:
            r['items'] = r['items'][:args.limit]
            r['rows'] = min(r['rows'], args.limit)
        results.append(r)
        sums.append(summarize(r))

    generated = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    for s in sums:
        print(_fmt_summary(s))
    tot_rows = sum(s['rows'] for s in sums)
    tot_fatal = sum(s['fatal_rows'] for s in sums)
    src_bad = sum(1 for r in results for it in (r.get('items') or [])
                  if SOURCE_STRICT & set(it.get('flags') or []))
    print('\n合計 %d 筆；致命 %d 筆；有旗標 %d 筆'
          % (tot_rows, tot_fatal, sum(s['flagged'] for s in sums)))

    out_path = ''
    if args.out:
        out_path = args.out if os.path.isabs(args.out) else os.path.join(
            B, args.out.replace('/', os.sep))
    json_path = ''
    if args.json not in (None, '-'):
        json_path = (args.json if os.path.isabs(args.json)
                     else os.path.join(B, args.json.replace('/', os.sep)))
    payload = {'generated': generated, 'source': '定稿/*.jsonl',
               'fatal_flags': sorted(FATAL), 'summary': sums,
               'results': results}
    if out_path:
        write_report(out_path, results, sums, generated)
        print('報告 → %s' % out_path)
    if args.json is not None:
        txt = json.dumps(payload, ensure_ascii=False, indent=1)
        if args.json == '-':
            print(txt)
        else:
            d = os.path.dirname(os.path.abspath(json_path))
            if d:
                os.makedirs(d, exist_ok=True)
            io.open(json_path, 'w', encoding='utf-8').write(txt)
            print('JSON → %s' % json_path)
    if args.strict_source and src_bad:
        print('（--strict-source）有 %d 筆 source 邊界旗標，rc=1' % src_bad)
        raise SystemExit(1)
    if (args.strict or args.strict_all) and tot_fatal:
        print('（--strict-all）有 %d 筆致命旗標，rc=1' % tot_fatal)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
