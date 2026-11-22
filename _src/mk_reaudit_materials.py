# -*- coding: utf-8 -*-
"""20K 再審材料：從 定稿/<book>.jsonl 打包約 20K 字的逐段再審材料（不呼叫 qwen）。

規格（AGENTS §7A）：
  - 來源唯一：定稿/<book>.jsonl；依 segments 拆 parts，不讀 docs／舊材料。
  - 每批不跨卷（--group-by vol，預設）；可改 --group-by chunk 鎖到分卷 chunk。
  - 疏＋記同 unit 不拆；unit 再長也不切。
  - 每檔 .md 約 19K–20.5K 字（--count-mode md，預設）；
    待審原文＋現譯約 11.5K–14K 字（--count-mode body 可改用原文＋現譯計量）。
  - 每段 `### [01]（key: …）`，段內交錯 `■ 段別（原文）[01]`／`■ 段別（現譯）[01]`。
  - 前文背景：前接原文 ≤1500 字＋前鄰現譯 ≤400 字；
    後文背景：後接原文 ≤600 字＋後鄰現譯 ≤300 字；資持記所釋鈔文 ≤2500 字。
  - 正文缺口：預設在缺口切檔（--gap-mode cut）；段內缺口或 --gap-mode note
    則於材料加【正文缺口提示】禁止代譯。同卷 raw 順序可疑 >5% 的書（戒疏）
    自動停用 gap 切檔，避免假缺口切出碎片檔。
  - 每檔另出 .json，記錄 idx/key/chunk/vol/raw_start/raw_end/labs/parts/src_hash/hash。

用法：
  python -X utf8 _src/mk_reaudit_materials.py --book 義鈔 --target-chars 20000 --check-raw
  python -X utf8 _src/mk_reaudit_materials.py --book 業疏 --out 測試/重譯/業疏/_再審
  python -X utf8 _src/mk_reaudit_materials.py --book 業疏 --check-raw --dry-run
"""
import argparse
import hashlib
import io
import json
import os
import re
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import book_config as BC  # noqa: E402

BOOKS = {
    '行事鈔': dict(id='xingshichao', jsonl='定稿/xingshichao.jsonl',
                 raw='TXT_句讀校定/xingshichao.txt',
                 alt='TXT/01_四分律刪繁補闕行事鈔.txt'),
    '戒疏': dict(id='jieshu', jsonl='定稿/jieshu.jsonl',
               raw='TXT_句讀校定/jieshu.txt',
               alt='TXT/02_四分律含注戒本疏.txt'),
    '業疏': dict(id='yeshu', jsonl='定稿/yeshu.jsonl',
               raw='TXT_句讀校定/yeshu.txt',
               alt='TXT/03_四分律刪補隨機羯磨疏.txt'),
    '尼鈔': dict(id='nicao', jsonl='定稿/nicao.jsonl',
               raw='TXT_句讀校定/nicao.txt',
               alt='TXT/04_四分律比丘尼鈔.txt'),
    '義鈔': dict(id='yichao', jsonl='定稿/yichao.jsonl',
               raw='TXT_句讀校定/yichao.txt',
               alt='TXT/05_四分律拾毗尼義鈔.txt'),
    # 資持記沒有對得上的 TXT 底本（定稿 raw 位移與 TXT_句讀校定 不同制）。
    '資持記': dict(id='zhichi', jsonl='定稿/zhichi.jsonl',
                raw='TXT_句讀校定/zhichi.txt', alt='', raw_reliable=False),
}

TARGET_CHARS = 10000
COUNT_MODES = ('md', 'body', 'source')
GROUP_BY = ('vol', 'chunk')
PRE_SRC_CAP = 1800
PRE_TR_CAP = 400
POST_SRC_CAP = 600
POST_TR_CAP = 300
MOTHER_CAP = 2500
GAP_MIN = 20
MD_TOL = 1.02
LABELS = ('疏文', '記文', '鈔文', '律文', '註文', '序文')
_HAN = re.compile(r'[\u4e00-\u9fff]')
_NUM_KEY = re.compile(r'^(\d+)([a-z]?)_([^_]+)_(\d+)(?:-(\d+))?$')
_PLAIN_NUM = re.compile(r'^(\d+)$')
_LAB_HEAD = re.compile(r'^【(?:疏文|記文|鈔文|律文|註文|序文)】\s*')

RA_PROMPT = BC.REAUDIT_PACK_PROMPT

NONBODY_HINTS = (
    '大覺慈父', '九十單提法', '百眾學法', '四分戒本》者', '甞聞毗尼藏', '原夫大雄',
    '疏卷第一', '四分律刪補', '四分律含注', '四分律拾毗尼', '四分律比丘尼鈔',
    '南山三大部', '底本', '目錄', '凡例', '科判', '校勘', '異體字',
)
DIRTY_MARKS = ('【後文背景', '【前文背景', '【必改硬傷】', '【逐句簡核】',
               '【分段核驗表】', '【本次待審單元】', '【本次待譯單元】',
               '【待審譯文】', '【目前譯文】', '【原文】', '【所釋鈔文', '【裁決')


# ---------------------------------------------------------------- 小工具
def han(s):
    return ''.join(_HAN.findall(s or ''))


def _h12(s):
    return hashlib.md5((s or '').encode('utf-8')).hexdigest()[:12]


def _read(path):
    return io.open(os.path.join(B, path.replace('/', os.sep)), encoding='utf-8').read()


def _exists(path):
    return os.path.exists(os.path.join(B, path.replace('/', os.sep)))


def _fmt(n):
    return '{:,}'.format(n)


def _now():
    import datetime
    return datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')


def default_out(book):
    return '測試/重譯/%s/_再審' % book


# ---------------------------------------------------------------- 定稿／原文載入
def load_raw(book):
    """回傳 (漢字流, 底本相對路徑)；無可用底本回 (None, '')。"""
    spec = BOOKS[book]
    if spec.get('raw_reliable') is False:
        return None, ''
    for key in ('raw', 'alt'):
        p = spec.get(key) or ''
        if p and _exists(p):
            return han(_read(p)), p
    return None, ''


def key_tuple(k):
    m = _NUM_KEY.match(k or '')
    if m:
        return (0, int(m.group(1)), m.group(2), m.group(3), int(m.group(4)),
                int(m.group(5) or 0))
    m = _PLAIN_NUM.match(k or '')
    if m:
        return (0, int(m.group(1)), '', '', 0, 0)
    return (1, 0, '', k or '', 0, 0)


def resolve_vol(units):
    chunk_vol = {}
    for u in units:
        if u['vol'] and u['chunk']:
            chunk_vol.setdefault(u['chunk'], u['vol'])
    for u in units:
        if u['vol']:
            continue
        v = chunk_vol.get(u['chunk'], '')
        if not v and u['chunk']:
            m = re.match(r'^(卷[一二三四五六七八九十上中下]+)', u['chunk'])
            if m:
                v = m.group(1)
        u['vol'] = v
    known = sorted([(u['raw_start'], u['vol']) for u in units if u['vol']],
                   key=lambda x: x[0])
    if not known:
        return units
    for u in units:
        if u['vol']:
            continue
        v = known[0][1]
        for a, vol in known:
            if a <= u['raw_start']:
                v = vol
            else:
                break
        u['vol'] = v
    return units


def vol_order(units):
    seq = []
    num = [u for u in units if key_tuple(u['key'])[0] == 0]
    for u in sorted(num, key=lambda u: key_tuple(u['key'])):
        if u['vol'] and u['vol'] not in seq:
            seq.append(u['vol'])
    for u in units:
        if u['vol'] and u['vol'] not in seq:
            seq.append(u['vol'])
    return seq


def canonical_order(units):
    """卷內：編號單位依 key 序；缺口單位（GAP 等）依 raw 位置插入。"""
    order = []
    for v in vol_order(units):
        grp = [u for u in units if u['vol'] == v]
        num = sorted([u for u in grp if key_tuple(u['key'])[0] == 0],
                     key=lambda u: key_tuple(u['key']))
        gaps = sorted([u for u in grp if key_tuple(u['key'])[0] != 0],
                      key=lambda u: (u['raw_start'], u['key']))
        gi = 0
        for u in num:
            while gi < len(gaps) and gaps[gi]['raw_start'] < u['raw_start']:
                order.append(gaps[gi])
                gi += 1
            order.append(u)
        order.extend(gaps[gi:])
    seen = set(id(u) for u in order)
    rest = [u for u in units if id(u) not in seen]
    rest.sort(key=lambda u: (u['raw_start'], u['key']))
    order.extend(rest)
    return order


def _monotonic_flags(order):
    last = {}
    for u in order:
        prev = last.get(u['vol'])
        u['mono'] = (prev is None) or (u['raw_start'] >= prev)
        if prev is None or u['raw_start'] > prev:
            last[u['vol']] = u['raw_start']
    return order


def dirty_hits(text):
    """偵測定稿殘留的材料區塊標記／行首 ■，供材料加註（不刪改原文）。"""
    hits = []
    t = text or ''
    for m in DIRTY_MARKS:
        if m in t:
            hits.append(m.lstrip('【'))
    if re.search(r'(?m)^\s*■\s', t):
        hits.append('行首■')
    if re.search(r'(?m)^\s*###\s', t):
        hits.append('行首###')
    return list(dict.fromkeys(hits))


def _parts_of(row):
    """定稿 segments → parts。雙欄（疏／記）必須逐段保留 lab／source／translation 對位，
    不可把兩欄合併成單欄；無 segments 時才退回頂層 label／source／translation。"""
    segs = row.get('segments') or []
    parts = []
    for s in segs:
        lab = s.get('label') or row.get('label') or '鈔文'
        orig = (s.get('source') or '').strip()
        tr = _LAB_HEAD.sub('', (s.get('translation') or '').strip())
        disp = (s.get('display_source') or '').strip()
        if not orig and not tr:
            continue
        parts.append({'lab': lab, 'orig': orig, 'tr': tr, 'display': disp})
    if not parts:
        lab = row.get('label') or '鈔文'
        orig = (row.get('source') or '').strip()
        tr = _LAB_HEAD.sub('', (row.get('translation') or '').strip())
        parts.append({'lab': lab, 'orig': orig, 'tr': tr,
                      'display': (row.get('display_source') or '').strip()})
    return parts


def _part_spans(unit, raw_h):
    """unit['raw_ok'] 只代表 source 與 raw 區間相符；part['raw_ok'] 代表 part 定位。"""
    a, b = unit['raw_start'], unit['raw_end']
    parts = unit['parts']
    hs = [han(p['orig']) for p in parts]
    unit_h = han(unit['row'].get('source', ''))
    unitsum = sum(len(x) for x in hs)
    unit['parts_joined'] = (unitsum == len(unit_h))
    if raw_h is None:
        unit['raw_ok'] = None
        for p in parts:
            p['start'] = p['end'] = -1
            p['raw_ok'] = None
        return unit
    unit['raw_ok'] = (0 <= a < b <= len(raw_h) and raw_h[a:b] == unit_h)
    if unit['raw_ok'] and unit['parts_joined']:
        cur = a
        for p, h in zip(parts, hs):
            p['start'], p['end'], p['raw_ok'] = cur, cur + len(h), True
            cur += len(h)
        return unit
    cur = a if a >= 0 else 0
    for p, h in zip(parts, hs):
        q = -1
        if 0 <= a < b <= len(raw_h):
            q = raw_h.find(h, max(0, a - 40), b) if h else -1
        if q >= 0:
            p['start'], p['end'] = q, q + len(h)
            p['raw_ok'] = (h == raw_h[q:q + len(h)])
            cur = q + len(h)
        else:
            p['start'], p['end'], p['raw_ok'] = cur, cur + len(h), False
            cur += len(h)
    return unit


def make_units(book, raw_h):
    rows = [json.loads(x) for x in
            io.open(os.path.join(B, BOOKS[book]['jsonl'].replace('/', os.sep)),
                    encoding='utf-8') if x.strip()]
    units = []
    for r in rows:
        parts = _parts_of(r)
        for p in parts:
            p['dirty_orig'] = dirty_hits(p['orig'])
            p['dirty_tr'] = dirty_hits(p['tr'])
            p['dirty'] = list(dict.fromkeys(p['dirty_orig'] + p['dirty_tr']))
        u = {
            'key': r.get('key') or '',
            'row': r,
            'chunk': r.get('chunk') or '',
            'vol': r.get('vol') or '',
            'raw_start': int(r.get('raw_start', -1) or -1),
            'raw_end': int(r.get('raw_end', -1) or -1),
            'labs': list(dict.fromkeys(p['lab'] for p in parts if p['lab'])),
            'parts': parts,
            'raw_ok': True,
            'dirty': list(dict.fromkeys(h for p in parts for h in p['dirty'])),
        }
        u['src_hash'] = _h12(han(r.get('source', '')))
        u['hash'] = _h12('|'.join(
            [u['key']] + ['%s\t%s\t%s' % (p['lab'], p['orig'], p['tr']) for p in parts]))
        _part_spans(u, raw_h)
        units.append(u)
    resolve_vol(units)
    return _monotonic_flags(canonical_order(units))


# ---------------------------------------------------------------- 背景與缺口
def _clip_tail(s, cap):
    s = (s or '').strip()
    if len(han(s)) <= cap:
        return s
    acc = 0
    idx = len(s)
    for i in range(len(s) - 1, -1, -1):
        if _HAN.match(s[i]):
            acc += 1
        if acc >= cap:
            idx = i
            break
    return '…' + s[idx:].lstrip()


def _clip_head(s, cap):
    s = (s or '').strip()
    if len(han(s)) <= cap:
        return s
    acc = 0
    for i, ch in enumerate(s):
        if _HAN.match(ch):
            acc += 1
        if acc >= cap:
            return s[:i + 1].rstrip() + '…'
    return s


def context_before(order, i0, pre_src=None, pre_tr=None):
    pre_src = PRE_SRC_CAP if pre_src is None else pre_src
    pre_tr = PRE_TR_CAP if pre_tr is None else pre_tr
    u0 = order[i0]
    src, tr = '', ''
    if i0 > 0 and order[i0 - 1]['vol'] == u0['vol']:
        tr = _clip_tail(order[i0 - 1]['parts'][-1]['tr'], pre_tr)
        buf, acc = [], 0
        for j in range(i0 - 1, -1, -1):
            if order[j]['vol'] != u0['vol']:
                break
            t = '\n'.join(p['orig'] for p in order[j]['parts'])
            buf.append(t)
            acc += len(han(t))
            if acc >= pre_src:
                break
        src = _clip_tail('\n'.join(reversed(buf)), pre_src)
    return src, tr


def context_after(order, i1, post_src=None, post_tr=None):
    post_src = POST_SRC_CAP if post_src is None else post_src
    post_tr = POST_TR_CAP if post_tr is None else post_tr
    u1 = order[i1]
    src, tr = '', ''
    if i1 + 1 < len(order) and order[i1 + 1]['vol'] == u1['vol']:
        tr = _clip_head(order[i1 + 1]['parts'][0]['tr'], post_tr)
        buf, acc = [], 0
        for j in range(i1 + 1, len(order)):
            if order[j]['vol'] != u1['vol']:
                break
            t = '\n'.join(p['orig'] for p in order[j]['parts'])
            buf.append(t)
            acc += len(han(t))
            if acc >= post_src:
                break
        src = _clip_head('\n'.join(buf), post_src)
    return src, tr


def _gap_kind(order, i, raw_h):
    a = order[i - 1]['raw_end']
    b = order[i]['raw_start']
    if raw_h is None or not (0 <= a < b <= len(raw_h)):
        return '正文'
    seg = raw_h[a:b]
    for hint in NONBODY_HINTS:
        if hint in seg:
            return '非正文'
    return '正文'


def _intra_gaps(unit):
    out = []
    parts = unit['parts']
    for p, q in zip(parts, parts[1:]):
        if 0 <= p.get('end', -1) < q.get('start', -1):
            n = q['start'] - p['end']
            if n >= GAP_MIN:
                out.append(n)
    return out


def unit_size(u, mode):
    src = sum(len(p['orig']) for p in u['parts'])
    if mode == 'source':
        return src
    return src + sum(len(p['tr']) for p in u['parts'])


# ---------------------------------------------------------------- 材料渲染
def mother_text(pack, book):
    """資持記：所釋鈔文（≤2500 字）；其他書回空字串。"""
    if book != '資持記':
        return ''
    try:
        import mother_corpus as MC
        # mother_corpus._seq_json() 每次呼叫都重讀 6MB JSON；本行程只快取一次。
        if not getattr(MC, '_RA_SEQ_READY', False):
            _seq = MC._seq_json()
            MC._seq_json = (lambda: _seq)
            MC._RA_SEQ_READY = True
        texts = [p['orig'] for u in pack for p in u['parts'] if (p.get('orig') or '').strip()]
        if not texts:
            return ''
        txt = MC.chao_for_units(texts) if len(texts) > 1 else MC.chao_for(texts[0])
        return _clip_head(txt or '', MOTHER_CAP)
    except Exception:
        return ''


# ---------------------------------------------------------------- 對照層（v2）
REF_CAP = 1400


SINGLE_SCOPE = (
    '### 範圍與讀法\n'
    '1. 本檔只含一個單位 [01]（單段送審）；核對範圍就是這一段，不得自行擴大或合併其他段落。\n'
    '2. 先遮蔽【現譯】單讀【原文】，獨立拆解文法、主客施受、條件界限與律義，再反向驗收【現譯】，'
    '切勿順著譯文流暢度讀過。\n'
    '3. 【前文背景】【後文背景】僅供銜接理解；【對照層】僅供校勘，兩者都嚴禁譯入正文。\n'
)


def _interlinear_notes(unit, cap=900):
    """原典雙行夾注：取 display_source 的〔…〕（CBETA 尼鈔 X40n0724 還原）。"""
    notes = []
    for p in unit['parts']:
        disp = p.get('display') or ''
        for m in re.finditer(r'〔([^〕]{2,})〕', disp):
            a = max(0, m.start() - 10)
            notes.append('%s〔%s〕' % (disp[a:m.start()].strip(), m.group(1).strip()))
    return '\n'.join(notes[:10])[:cap]


def _plain_src(unit):
    return '\n'.join(p['orig'] for p in unit['parts'] if (p.get('orig') or '').strip())


def _parallel_notes(book, src, cap=900, limit=2):
    """書庫平行釋文：優先同宗註疏（戒疏／行宗記／資持記／行事鈔／婆沙）。"""
    try:
        import local_corpus as LC
    except Exception:
        return ''
    q = han(src)[:14]
    if len(q) < 6:
        return ''
    try:
        hits = LC.find(q, None, limit=limit, pad=150,
                       ctx_book=('義鈔' if book == '義鈔' else book))
    except Exception:
        return ''
    out = []
    for h in hits or []:
        b = h.get('book') or ''
        if b == book or b in ('義鈔輔要記',):
            continue
        kw = (h.get('kwic') or '').strip()
        if kw:
            out.append('《%s》%s：%s' % (b, h.get('juan') or '', kw))
    return '\n'.join(out)[:cap]


# ---------------------------------------------------------------- 通用對照檢索（無題庫詞）
_DF_BOOKS = ('戒疏', '行宗記', '資持記', '行事鈔')
_DF_TEXT = {}
_STOP_CHARS = set(
    '的了著是在把被將與及或而則以於之其此彼所為無有不得應須當如若使皆並又即乃'
    '但故也矣焉哉乎者我汝今昔上下前後中內外一二三四五六七八九十百千萬如是云何')
_STOP_WORDS = {'如是', '云何', '所以', '其中', '今此', '若爾', '何故', '何以',
               '故知', '所言', '問曰', '答曰', '若言', '此中', '爾時', '一時'}


def _df_texts():
    """四部註疏的漢字流（只建一次，供 DF 稀有度評分）。"""
    if _DF_TEXT:
        return _DF_TEXT
    import local_corpus as LC
    LC.load()
    for b in _DF_BOOKS:
        _DF_TEXT[b] = ''.join(LC._plain(x['text']) for x in LC.LINES
                              if x.get('book') == b)
    return _DF_TEXT


def _sentences(src):
    return [s for s in re.split(r'[。！？；：\n]', src or '')
            if len(han(s)) >= 6]


def _sampled_sentences(src, per=2):
    ss = _sentences(src)
    if len(ss) <= per * 3:
        return ss
    n = len(ss)
    return ss[:per] + ss[n // 2 - per // 2:n // 2 + per - per // 2] + ss[-per:]


def _grams(sentence, ns=(2, 3)):
    h = han(sentence)
    out = set()
    for n in ns:
        for i in range(0, max(0, len(h) - n + 1)):
            g = h[i:i + n]
            if g in _STOP_WORDS:
                continue
            if all(c in _STOP_CHARS for c in g):
                continue
            out.add(g)
    return out


def _yichao_parallel(src, cap=1400, limit=3):
    """義鈔：通用演算法。切句→前中後取樣→2/3 字候選→四庫 DF 稀有度→雙詞共現查四庫。"""
    try:
        texts = _df_texts()
        import local_corpus as LC
    except Exception:
        return ''
    # 1) 取樣句與候選
    cands = set()
    for s in _sampled_sentences(src):
        cands |= _grams(s)
    if not cands:
        return ''
    # 2) 四庫 DF／總頻次評分（低頻優先，長詞優先）
    scored = []
    for g in cands:
        if len(g) < 2:
            continue
        cnt = 0
        df = 0
        for b in _DF_BOOKS:
            t = texts.get(b) or ''
            c = t.count(g)
            cnt += c
            if c:
                df += 1
        # 2–3 字都要在四庫有一定出現次數，避免「是上」「畜是」跨詞偽雙字
        if cnt < 5:
            continue
        score = cnt / (1.6 if len(g) >= 3 else 1.0)  # 3 字加權（較不易撞詞）
        scored.append((score, -len(g), g))
    scored.sort()
    top = [x[2] for x in scored[:14]]
    rank = {g: i for i, g in enumerate(top)}
    # 3) 每句取「最稀有且不重疊」的兩詞作共現查詢（最多 8 組），不先 break
    pairs, seen_p = [], set()
    for s in _sampled_sentences(src):
        h = han(s)
        spans = []
        for g in set(_grams(s)):
            if g not in rank:
                continue
            a0 = h.find(g)
            if a0 >= 0:
                spans.append((rank[g], a0, a0 + len(g), g))
        spans.sort()
        chosen = []
        for _r, a0, a1, g in spans:
            if all(a1 <= b0 or a0 >= b1 for _, b0, b1, _ in chosen):
                chosen.append((_r, a0, a1, g))
            if len(chosen) == 2:
                break
        if len(chosen) == 2:
            a, b = chosen[0][3], chosen[1][3]
            if a != b and (a, b) not in seen_p:
                seen_p.add((a, b))
                pairs.append((a, b))
        if len(pairs) >= 8:
            break
    # 4) 每組跨四庫查，收集不同書的命中
    out, seen_hit = [], set()
    for a, b in pairs:
        for work in _DF_BOOKS:
            try:
                hs = LC.find('%s %s' % (a, b), work, limit=1, pad=200)
            except Exception:
                hs = []
            for h in hs:
                kw = (h.get('kwic') or '').strip()
                sig = (h.get('book'), kw[:40])
                if not kw or sig in seen_hit:
                    continue
                seen_hit.add(sig)
                out.append('《%s》%s（%s＋%s）：%s'
                           % (h.get('book'), h.get('juan') or '', a, b, kw))
                break
            if len(out) >= limit:
                break
        if len(out) >= limit:
            break
    # 5) 共現查無（長問答常見）：退回稀有單詞跨四庫查
    if not out:
        for g in top[:6]:
            for work in _DF_BOOKS:
                try:
                    hs = LC.find(g, work, limit=1, pad=220)
                except Exception:
                    hs = []
                got = False
                for h in hs or []:
                    kw = (h.get('kwic') or '').strip()
                    sig = (h.get('book'), kw[:40])
                    if not kw or sig in seen_hit:
                        continue
                    seen_hit.add(sig)
                    out.append('《%s》%s（%s）：%s'
                               % (h.get('book'), h.get('juan') or '', g, kw))
                    got = True
                    break
                if got or len(out) >= limit:
                    break
            if len(out) >= limit:
                break
    return '\n'.join(out)[:cap]


# ---------------------------------------------------------------- 辭典自動索引（無題庫詞）
_DICT_INDEX = None


def _dict_index():
    """《南山律學辭典》詞頭＋4-gram 稀有片段 Counter；只建一次。"""
    global _DICT_INDEX
    if _DICT_INDEX is not None:
        return _DICT_INDEX
    p = os.path.join(B, '原文', '南山律學辭典', '南山律學辭典.txt')
    t = io.open(p, encoding='utf-8', errors='ignore').read() if os.path.exists(p) else ''
    heads = set(m.group(1).strip() for m in re.finditer(r'【([^】]{2,12})】', t))
    for ln in t.splitlines():
        s = ln.strip()
        if 2 <= len(s) <= 8 and not re.search(r'[，。；：！？、（）]', s):
            heads.add(s)
    from collections import Counter
    h = han(t)
    four = Counter(h[i:i + 4] for i in range(0, max(0, len(h) - 3)))
    _DICT_INDEX = (t, heads, four)
    return _DICT_INDEX


def _dict_notes(src, cap=1100):
    """只留真實辭典詞頭＋罕見 4-gram（1–4 次）；依稀有度＋長度排序，最多 4 條。"""
    t, heads, four = _dict_index()
    if not t:
        return ''
    h = han(src)
    cand = set()
    for n in (2, 3, 4):
        for i in range(0, max(0, len(h) - n + 1)):
            w = h[i:i + n]
            if all(c in _STOP_CHARS for c in w):
                continue
            cand.add(w)
    scored = []
    for w in cand:
        if len(w) == 4:
            cnt = four.get(w, 0)
            if not (1 <= cnt <= 4) and w not in heads:
                continue
        elif w in heads:
            cnt = four.get(w, 1) if len(w) == 4 else 1
        else:
            continue
        if w in _STOP_WORDS:
            continue
        scored.append((cnt, -len(w), w))
    scored.sort()
    out, used = [], 0
    for cnt, neglen, w in scored:
        i = t.find(w)
        if i < 0:
            continue
        ctx = re.sub(r'\s+', ' ', t[max(0, i - 90):i + 300]).strip()
        # 辭典排版常在中文間換行；接回以免檢索詞被空白切開
        ctx = re.sub(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])', '', ctx)
        out.append('「%s」：%s' % (w, ctx))
        used += 1
        if used >= 4:
            break
    return '\n'.join(out)[:cap]


_KE_FILES = {'業疏': '業疏科', '戒疏': '戒疏科'}


def _ke_volume_excerpt(book, chunk, cap=1200):
    """依卷／子卷比例，從科判檔取該區間節錄（用於引號查不到的上層母科）。"""
    name = _KE_FILES.get(book)
    if not name:
        return ''
    p = os.path.join(B, '原文', name, name + '.txt')
    if not os.path.exists(p):
        return ''
    m = re.match(r'卷([一二三四])(?:之([一二三四五六]))?', chunk or '')
    if not m:
        return ''
    t = io.open(p, encoding='utf-8', errors='ignore').read()
    vol = '卷' + m.group(1)
    _CN = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6}
    sub = _CN.get(m.group(2) or '一', 1)
    marks = [(x.start(), x.group(0)) for x in re.finditer(r'卷[一二三四]', t)]
    start = None
    end = len(t)
    for pos, txt in marks:
        if txt == vol and start is None:
            start = pos
        elif start is not None and pos > start:
            end = pos
            break
    if start is None or end <= start:
        return ''
    a = start + int((end - start) * (sub - 1) / 6.0)
    b = start + int((end - start) * sub / 6.0)
    seg = re.sub(r'[ \t\r]+', ' ', t[a:b]).strip()
    return seg[:cap]


def _ke_note(book, src, chunk='', key='', cap=420):
    """科判位置：優先用 key 的『卷X之Y』取該卷區間節錄；再以引號內科文／原文頭查科檔。"""
    m = re.search(r'(卷[一二三四]之[一二三四五六])', key or '')
    label = m.group(1) if m else (chunk or '')
    seg = _ke_volume_excerpt(book, label, cap=min(cap, 1200))
    if seg and len(han(seg)) >= 12:
        return '（%s區間節錄）%s' % (label or '', seg)
    try:
        import local_corpus as LC
        work = _KE_FILES.get(book, '')
        if not work:
            return ''
        cands = []
        for q in re.findall(r'「([^」]{2,14})」', src):
            q = q.strip()
            if len(q) >= 2:
                cands.append(q)
        cands.append(han(src)[:14])
        for q in cands:
            if len(q) < 2:
                continue
            hits = LC.find(q, work, limit=1, pad=220)
            if not hits:
                continue
            kw = (hits[0].get('kwic') or '').strip()
            if not kw:
                continue
            return ('《%s》%s：%s' % (hits[0].get('book'),
                                     hits[0].get('juan') or '', kw)).strip()[:cap]
    except Exception:
        return ''
    return ''


def _suoshu_text(order, i, cap=1200):
    """單邊記文（含 JE-/YE-/GAP/BLIND 殘片）：往前找同一卷最近的【疏文】，作為【所釋疏文】。

    已含【疏文】的雙欄單位不重複掛（那屬雙向對賬，不是單邊記文）。
    """
    u = order[i]
    _is_ji = any(p['lab'] == '記文' and (p.get('orig') or '').strip()
                 for p in u['parts'])
    _has_su = any(p['lab'] == '疏文' and (p.get('orig') or '').strip()
                  for p in u['parts'])
    _gap = bool(re.match(r'(?:JE|YE|GAP|BLIND)', u['key'] or ''))
    # 單邊記文＝只有記文沒有疏文；缺口殘片（JE/YE/GAP/BLIND）即使是單欄也掛，
    # 但已同時含疏＋記的雙欄單位不重複掛。
    if not ((_is_ji and not _has_su) or (_gap and not (_has_su and _is_ji))):
        return ''
    for j in range(i - 1, max(-1, i - 10), -1):
        v = order[j]
        if u['vol'] and v['vol'] and v['vol'] != u['vol']:
            break
        if v['raw_start'] >= u['raw_start'] and u['raw_start'] > 0:
            continue
        if u['raw_start'] > 0 and v['raw_end'] >= 0 \
                and u['raw_start'] - v['raw_end'] > 6000:
            continue
        sus = [p['orig'] for p in v['parts']
               if p['lab'] == '疏文' and (p.get('orig') or '').strip()]
        if sus:
            return _clip_tail('\n'.join(sus), cap)
    return ''


def reference_blocks(book, unit, order, i):
    """回傳 [(標題, 內文)]：只掛本段可用且有據的對照層。"""
    blocks = []
    src = _plain_src(unit)
    if book == '尼鈔':
        notes = _interlinear_notes(unit)
        if notes:
            blocks.append((
                '原典雙行夾注（CBETA X40n0724；〔…〕內為夾注）',
                '下列夾注皆為原典所有，譯文以圓括號（）對譯者必須保留，'
                '不得當作「自加解說括號」刪除；亦不得把夾注內容改寫成正文。\n' + notes))
    if book == '行事鈔':
        try:
            import mother_corpus as MC
            if not getattr(MC, '_RA_SEQ_READY', False):
                _seq = MC._seq_json()
                MC._seq_json = (lambda: _seq)
                MC._RA_SEQ_READY = True
            ji = MC.ji_for_chao(src, cap=2200)
        except Exception:
            ji = ''
        if ji:
            blocks.append(('資持記相關釋文（僅供訓釋字義，嚴禁搬入正文）', ji))
        # 鈔文問「何法」而資持記以部派受戒釋之：母本序列比對不到時，
        # 以原文詞檢索資持記，取含「何部」的解說（不寫死該句）。
        if ('何法' in src or '三衣' in src) and '何部' not in (ji or ''):
            try:
                import local_corpus as LC
                for q in ('何法', '三衣'):
                    if q not in src:
                        continue
                    hits = LC.find(q, '資持記', limit=10, pad=600)
                    got = ''
                    for h in hits or []:
                        kw = (h.get('kwic') or '')
                        i = kw.find('何部')
                        if i >= 0:
                            got = kw[max(0, i - 200):i + 300].strip()
                            break
                    if got:
                        blocks.append((
                            '資持記相關釋文（原文詞檢索補查；僅供訓釋，嚴禁搬入正文）',
                            got[:900]))
                        break
            except Exception:
                pass
    if book == '義鈔':
        disp = '\n'.join(p.get('display') or '' for p in unit['parts']
                         if (p.get('display') or '').strip())
        if not disp:
            disp = (unit.get('row') or {}).get('display_source') or ''
        if disp and han(disp):
            blocks.append(('原典補標點原文（僅供斷句對照）', disp[:REF_CAP]))
        par = _yichao_parallel(src)
        if par:
            blocks.append(('平行釋文（戒疏／行宗記／資持記／行事鈔；僅供訓釋，嚴禁搬入正文）', par))
    if book in ('業疏', '戒疏'):
        sus = _suoshu_text(order, i)
        if sus:
            blocks.append(('所釋疏文（單邊記文之母文，僅供對讀，嚴禁抄入記文）', sus))
        ke = _ke_note(book, src, unit.get('chunk') or '', unit.get('key') or '')
        if ke:
            blocks.append(('所屬科判位置（僅供定位，勿改寫正文）', ke))
        if book == '戒疏' and ('文云' in src or '注云' in src):
            try:
                import local_corpus as LC
                q = han(src)[:12]
                hits = LC.find(q, '含注戒本', limit=1, pad=120)
                if hits:
                    blocks.append(('《含注戒本》對照（文云／注云出處）',
                                   ('%s：%s' % (hits[0].get('juan') or '',
                                                hits[0].get('kwic') or '')).strip()))
            except Exception:
                pass
    if book in ('戒疏', '業疏', '義鈔', '行事鈔'):
        dn = _dict_notes(src)
        if dn:
            blocks.append(('南山律學辭典條目參考（僅供訓釋，嚴禁搬入正文）', dn))
    return blocks


def render_material(book, pack, idx, book_id, key, pre, post, gaps, mode, raws,
                    mother='', refs=None):
    vol = pack[0]['vol'] or '（未分卷）'
    n = len(pack)
    src_chars = sum(len(p['orig']) for u in pack for p in u['parts'])
    tr_chars = sum(len(p['tr']) for u in pack for p in u['parts'])
    labs = sorted({p['lab'] for u in pack for p in u['parts']})
    src_all = '\n'.join(p['orig'] for u in pack for p in u['parts'])
    tr_all = '\n'.join(p['tr'] for u in pack for p in u['parts'])
    long_ = any(re.search(r'_L\d{3,}', u['key']) for u in pack) \
        or '（本段前文）' in src_all or '（本段後文）' in src_all
    notes = BC.notes_for(book, labs, src_all, tr_all, long=long_,
                         key=pack[0]['key'])
    prompt = BC.render(BC.REAUDIT_PACK_PROMPT_TMPL,
                       scope_note=(SINGLE_SCOPE if n == 1 else BC.PACK_SCOPE),
                       **notes)
    L = [prompt, '', '---', '',
         '（出處：《%s》%s，%s｜單位 %d–%d｜原文 %s 字＋現譯 %s 字）'
         % (book, vol, key, 1, n, _fmt(src_chars), _fmt(tr_chars)), '']
    _gaps_body = [g for g in gaps if g['kind'] == '正文']
    if _gaps_body:
        L += ['【正文缺口提示】', '',
              '（本檔前／後／段間有正文缺口共 %s 字：%s；此係定稿未收錄之正文，'
              '禁止代譯、補譯或憑上下文虛構，亦不得據此判定現譯漏譯。）'
              % (_fmt(sum(g['chars'] for g in _gaps_body)),
                 '、'.join('%s→%s %d字' % (g['after'], g['before'], g['chars'])
                          for g in _gaps_body)), '']
    L += ['【前文背景（僅供參考，嚴禁譯入正文）】', '']
    if pre[0].strip():
        L += ['■ 原文（前接）', '', pre[0], '']
    if pre[1].strip():
        L += ['■ 前鄰現譯', '', pre[1], '']
    if not pre[0].strip() and not pre[1].strip():
        L += ['（本卷開頭，無前文背景）', '']
    if refs:
        L += ['【對照層（僅供校勘，嚴禁譯入正文）】', '']
        for title, body in refs:
            if not (body or '').strip():
                continue
            L += ['■ %s' % title, '', body.strip(), '']
    _dirty = [(i, u) for i, u in enumerate(pack, 1) if u.get('dirty')]
    if _dirty:
        L += ['【定稿殘留提示】', '',
              '下列單位的原文／現譯含材料區塊殘留標記（逐字照錄，未刪改）：%s。'
              '請一併判定現譯是否誤將背景或清單混入正文，並於【必改硬傷】點名。'
              % '、'.join('[%02d]（%s）' % (i, '／'.join(u['dirty'])) for i, u in _dirty), '']
    L += ['【本次待審單元】', '']
    for i, u in enumerate(pack, 1):
        tag = '[%02d]' % i
        L += ['### %s（key: %s）' % (tag, u['key']), '']
        for p in u['parts']:
            L += ['■ %s（原文）%s' % (p['lab'], tag), '']
            if p.get('dirty_orig'):
                L += ['〔定稿殘留：此段含 %s；逐字照錄〕' % '／'.join(p['dirty_orig']), '']
            L += [p['orig'].strip(), '']
            L += ['■ %s（現譯）%s' % (p['lab'], tag), '']
            if p.get('dirty_tr'):
                L += ['〔定稿殘留：此段含 %s；逐字照錄〕' % '／'.join(p['dirty_tr']), '']
            L += [p['tr'].strip(), '']
    L += ['【後文背景（僅供參考，嚴禁譯入正文）】', '']
    if post[0].strip():
        L += ['■ 原文（後接）', '', post[0], '']
    if post[1].strip():
        L += ['■ 後鄰現譯', '', post[1], '']
    if not post[0].strip() and not post[1].strip():
        L += ['（本卷末尾，無後文背景）', '']
    if mother:
        L += ['【所釋鈔文（僅供對照，嚴禁譯入正文）】', '', mother, '']
    return '\n'.join(L)


def _unit_json(idx, u):
    parts = []
    for p in u['parts']:
        parts.append({
            'lab': p['lab'],
            'orig': p['orig'],
            'tr': p['tr'],
            'src_len': len(p['orig']),
            'tr_len': len(p['tr']),
            'src_han': len(han(p['orig'])),
            'tr_han': len(han(p['tr'])),
            'start': p.get('start', -1),
            'end': p.get('end', -1),
            'raw_ok': p.get('raw_ok'),
            'dirty': list(p.get('dirty') or []),
            'dirty_orig': list(p.get('dirty_orig') or []),
            'dirty_tr': list(p.get('dirty_tr') or []),
            'src_hash': _h12(p['orig']),
            'hash': _h12('%s\t%s' % (p['orig'], p['tr'])),
        })
    return {
        'idx': idx,
        'key': u['key'],
        'chunk': u['chunk'],
        'vol': u['vol'],
        'raw_start': u['raw_start'],
        'raw_end': u['raw_end'],
        'labs': u['labs'],
        'parts': parts,
        'src_hash': u.get('src_hash') or _h12(
            han((u.get('row') or {}).get('source', '')) or
            ''.join(p['orig'] for p in u['parts'])),
        'hash': u['hash'],
        'raw_ok': u.get('raw_ok'),
        'parts_joined': bool(u.get('parts_joined', True)),
        'dirty': list(u.get('dirty') or []),
        'chars': unit_size(u, 'body'),
    }


def _render_len(book, pack, order, gap_mode, gap_min, raw_h, mode):
    """估算/實測材料長度；mode=md 時回傳整份 .md 字數（含資持記母本預留）。"""
    if mode != 'md':
        return sum(unit_size(u, mode) for u in pack)
    i0 = order.index(pack[0])
    i1 = order.index(pack[-1])
    pre = context_before(order, i0)
    post = context_after(order, i1)
    gaps = _pack_gaps(pack, order, gap_mode, gap_min, raw_h)
    txt = render_material(book, pack, 1, BOOKS[book]['id'],
                          'x' * (len(BOOKS[book]['id']) + 7), pre, post, gaps,
                          mode, raw_h, mother='')
    # 資持記母本在 emit 時才真正取用，這裡先預留上限，避免超長。
    return len(txt) + (MOTHER_CAP if book == '資持記' else 0)


# ---------------------------------------------------------------- 缺口收集
def _pack_gaps(pack, order, gap_mode, gap_min, raw_h):
    if gap_mode == 'off':
        return []
    gaps = []
    i0 = order.index(pack[0])
    i1 = order.index(pack[-1])
    if i0 > 0:
        prev = order[i0 - 1]
        n = pack[0]['raw_start'] - prev['raw_end']
        if prev['vol'] == pack[0]['vol'] and n >= gap_min and prev.get('mono') \
                and pack[0].get('mono'):
            gaps.append({'chars': n, 'after': prev['key'], 'before': pack[0]['key'],
                         'kind': _gap_kind(order, i0, raw_h), 'where': 'before'})
    if i1 + 1 < len(order):
        nxt = order[i1 + 1]
        n = nxt['raw_start'] - pack[-1]['raw_end']
        if nxt['vol'] == pack[-1]['vol'] and n >= gap_min and nxt.get('mono') \
                and pack[-1].get('mono'):
            gaps.append({'chars': n, 'after': pack[-1]['key'], 'before': nxt['key'],
                         'kind': _gap_kind(order, i1 + 1, raw_h), 'where': 'after'})
    for a, b in zip(pack, pack[1:]):
        n = b['raw_start'] - a['raw_end']
        if a['vol'] == b['vol'] and n >= gap_min and a.get('mono') and b.get('mono'):
            gaps.append({'chars': n, 'after': a['key'], 'before': b['key'],
                         'kind': _gap_kind(order, order.index(b), raw_h),
                         'where': 'inside'})
    for u in pack:
        for n in _intra_gaps(u):
            gaps.append({'chars': n, 'after': u['key'], 'before': u['key'],
                         'kind': '正文', 'where': 'inside'})
    return gaps


def build_packs(book, order, target, mode, gap_mode, gap_min, raw_h, group_by):
    packs, cur = [], []
    for i, u in enumerate(order):
        gap = None
        if cur:
            prev = cur[-1]
            same_vol = prev['vol'] == u['vol']
            n = u['raw_start'] - prev['raw_end'] if same_vol else 0
            if same_vol and n >= gap_min and prev.get('mono') and u.get('mono'):
                gap = {'chars': n, 'after': prev['key'], 'before': u['key'],
                       'kind': _gap_kind(order, i, raw_h), 'where': 'between'}
        boundary = bool(cur) and (
            cur[-1]['vol'] != u['vol']
            or (group_by == 'chunk' and cur[-1]['chunk'] != u['chunk']))
        _cut_gap = bool(gap) and gap['kind'] == '正文' and gap_mode == 'cut' \
            and key_tuple(u['key'])[0] == 0 and key_tuple(prev['key'])[0] == 0
        if cur and (boundary or _cut_gap):
            packs.append(cur)
            cur = []
        if cur:
            trial = cur + [u]
            if _render_len(book, trial, order, gap_mode, gap_min, raw_h,
                           mode) > target * (MD_TOL if mode == 'md' else 1.0):
                packs.append(cur)
                cur = []
        cur.append(u)
    if cur:
        packs.append(cur)
    return packs


# ---------------------------------------------------------------- 輸出
def emit_pack(outdir, pack, idx, book, book_id, mode, gaps, raws,
              pre=None, post=None, parent='', part='', key='', target=TARGET_CHARS,
              refs=None):
    key = key or '%s_r%04d' % (book_id, idx)
    pre = pre if pre is not None else ('', '')
    post = post if post is not None else ('', '')
    mother = mother_text(pack, book)
    md = render_material(book, pack, idx, book_id, key, pre, post, gaps, mode,
                         raws, mother, refs=refs)
    io.open(os.path.join(outdir, key + '.md'), 'w', encoding='utf-8').write(md)
    units_json = [_unit_json(i, u) for i, u in enumerate(pack, 1)]
    meta = {
        'key': key,
        'book': book,
        'book_id': book_id,
        'vol': pack[0]['vol'],
        'chunk': pack[0]['chunk'],
        'chunks': list(dict.fromkeys(u['chunk'] for u in pack)),
        'raw_start': min(u['raw_start'] for u in pack),
        'raw_end': max(u['raw_end'] for u in pack),
        'target_chars': target,
        'count_mode': mode,
        'chars': {
            'src': sum(len(p['orig']) for u in pack for p in u['parts']),
            'tr': sum(len(p['tr']) for u in pack for p in u['parts']),
            'total': sum(unit_size(u, 'body') for u in pack),
        },
        'md_chars': len(md),
        'md_bytes': len(md.encode('utf-8')),
        'gaps': gaps,
        'raw_verified': bool(raws),
        'dirty_units': [i for i, u in enumerate(pack, 1) if u.get('dirty')],
        'prev_unit': pack[0].get('prev_key', ''),
        'next_unit': pack[-1].get('next_key', ''),
        'pre_src': pre[0], 'pre_tr': pre[1],
        'post_src': post[0], 'post_tr': post[1],
        'mother': mother,
        'refs': [t for t, _b in (refs or [])],
        'parent': parent, 'part': part,
        'units': units_json,
        'hash': _h12('|'.join(u['hash'] for u in pack)),
    }
    io.open(os.path.join(outdir, key + '.json'), 'w', encoding='utf-8').write(
        json.dumps(meta, ensure_ascii=False, indent=1))
    return key, meta


def _safe_key(k):
    return re.sub(r'[^\w\u4e00-\u9fff.-]', '_', str(k))


def generate_single(book, outdir, keys, pre_cap=PRE_SRC_CAP, post_cap=POST_SRC_CAP,
                    check_raw=False, force=False, verbose=True):
    """單段材料（v2）：每個 key 一份 .md／.json，附前後文與對照層。

    - 前文 ≤pre_cap（預設 1800）、後文 ≤post_cap（預設 600）。
    - 尼鈔：原典雙行夾注（display_source〔…〕）；行事鈔：資持記相關釋文；
      義鈔：補標點原文＋平行釋文；業疏／戒疏：所釋疏文＋科判。
    - 雙欄逐段對位（mk_reaudit._parts_of 保留 lab/source/translation）。
    """
    raws = load_raw(book)
    raw_h = raws[0]
    order = make_units(book, raw_h)
    pos = {u['key']: i for i, u in enumerate(order)}
    missing = [k for k in keys if k not in pos]
    if missing:
        raise SystemExit('以下 key 不在定稿 %s：%s' % (book, missing[:10]))
    os.makedirs(outdir, exist_ok=True)
    bid = BOOKS[book]['id']
    rep = os.path.join(outdir, '回覆')
    if os.path.isdir(rep) and any(f.endswith('_回.txt') for f in os.listdir(rep)) and not force:
        raise SystemExit('（已中止）輸出目錄已有回覆：%s；請加 --force 或換目錄' % outdir)
    for f in list(os.listdir(outdir)):
        if f.endswith(('.md', '.json')) and (
                f.startswith(bid + '_') or f.startswith('索引_')
                or f == '_材料索引.md'):
            try:
                os.remove(os.path.join(outdir, f))
            except OSError:
                pass
    metas, bad_units, bad_parts, disorder = [], [], [], []
    for n, k in enumerate(keys, 1):
        i = pos[k]
        u = order[i]
        pre = context_before(order, i, pre_cap, PRE_TR_CAP)
        post = context_after(order, i, post_cap, POST_TR_CAP)
        refs = reference_blocks(book, u, order, i)
        key = '%s_%s' % (bid, _safe_key(k))
        _, meta = emit_pack(outdir, [u], n, book, bid, 'body', [], raw_h,
                            pre=pre, post=post, key=key, target=0, refs=refs)
        meta['sample_key'] = k
        meta['n_units'] = 1
        meta['refs'] = [t for t, _b in refs]
        io.open(os.path.join(outdir, key + '.json'), 'w', encoding='utf-8').write(
            json.dumps(meta, ensure_ascii=False, indent=1))
        metas.append(meta)
        if u.get('raw_ok') is False:
            bad_units.append(u)
        for p in u['parts']:
            if p.get('raw_ok') is False:
                bad_parts.append((u, p))
        if not u.get('mono'):
            disorder.append(u)
        if verbose:
            print('  %-42s 原文 %4d／現譯 %4d｜前文 %4d／後文 %3d｜對照 %s'
                  % (key, len(han((u.get('row') or {}).get('source', ''))),
                     sum(len(p['tr']) for p in u['parts']), len(pre[0]), len(post[0]),
                     '、'.join(meta['refs']) or '—'))
    json.dump({'generated': _now(), 'book': book, 'book_id': bid, 'single': True,
               'pre_cap': pre_cap, 'post_cap': post_cap,
               'n': len(metas), 'keys': keys,
               'packs': [{k: m[k] for k in ('key', 'sample_key', 'vol', 'chunk',
                                            'raw_start', 'raw_end', 'chars',
                                            'md_chars', 'refs')} for m in metas]},
              io.open(os.path.join(outdir, '索引_%s.json' % bid), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    _write_raw_check(outdir, book, raws, order, bad_units, bad_parts,
                     disorder, raws[1])
    L = ['# 單段材料索引（%s）' % book, '',
         '- 來源：`定稿/%s.jsonl`（只讀）' % bid,
         '- 每段一份 `.md`／`.json`；前文 ≤%d、後文 ≤%d。' % (pre_cap, post_cap),
         '- 對照層：' + ('尼鈔原典夾注／行事鈔資持記釋文／義鈔輔要記平行與標點原文／'
                        '業疏戒疏所釋疏文與科判'), '',
         '| # | key | 卷 | 原文 | 現譯 | md | 對照層 |',
         '|--:|:--|:--|--:|--:|--:|:--|']
    for n, m in enumerate(metas, 1):
        L.append('| %d | %s | %s | %d | %d | %d | %s |'
                 % (n, m.get('sample_key'), m.get('vol'),
                    m['chars']['src'], m['chars']['tr'], m['md_chars'],
                    '、'.join(m.get('refs') or []) or '—'))
    io.open(os.path.join(outdir, '_材料索引_%s.md' % bid), 'w', encoding='utf-8').write(
        '\n'.join(L) + '\n')
    if verbose:
        print('已產生 %d 份單段材料 → %s' % (len(metas), outdir))
    return {'book': book, 'n': len(metas), 'packs': metas,
            'bad_units': len(bad_units), 'bad_parts': len(bad_parts),
            'disorder': len(disorder), 'raw': bool(raw_h)}


def _write_raw_check(outdir, book, raws, order, bad_units, bad_parts,
                     disorder, raw_path):
    joined_bad = [u for u in order if u.get('parts_joined') is False]
    L = ['# 原文核驗（%s）' % book, '',
         '- 原文底本：%s' % (raw_path or '（無）'),
         '- 漢字流長度：%s' % ((_fmt(len(raws[0])) if raws and raws[0]
                             else '（無底本，raw 驗證 unavailable）')),
         '- 單位總數：%s' % _fmt(len(order)),
         '- source 與 raw 區間相符：%s' % _fmt(len(order) - len(bad_units)),
         '- source 與 raw 區間不符：%s' % _fmt(len(bad_units)),
         '- parts 拼接與 unit source 不一致：%s' % _fmt(len(joined_bad)),
         '- part 無法在 raw 內定位：%s' % _fmt(len(bad_parts)),
         '- 同卷 raw_start 非單調（定位可疑）：%s' % _fmt(len(disorder)),
         '']
    if bad_units:
        L += ['## source／raw 不符（前 50）', '',
              '| key | raw_start | raw_end | 定稿 source 起頭 | 底本同位起頭 |',
              '|:--|--:|--:|:--|:--|']
        for u in bad_units[:50]:
            a, b = u['raw_start'], u['raw_end']
            got = raws[0][a:b][:30] if raws and 0 <= a < b <= len(raws[0]) else ''
            L.append('| %s | %s | %s | %s | %s |'
                     % (u['key'], a, b, han(u['row'].get('source', ''))[:30], got))
        L.append('')
    if bad_parts:
        L += ['## parts 無法定位（前 50）', '',
              '| key | 段別 | part 原文起頭 |', '|:--|:--|:--|']
        for u, p in bad_parts[:50]:
            L.append('| %s | %s | %s |' % (u['key'], p['lab'], han(p['orig'])[:30]))
        L.append('')
    if joined_bad:
        L += ['## parts 拼接 ≠ unit source（前 50）', '',
              '| key | 段別 | 差異 |', '|:--|:--|--:|']
        for u in joined_bad[:50]:
            d = sum(len(han(p['orig'])) for p in u['parts']) - len(han(u['row'].get('source', '')))
            L.append('| %s | %s | %+d |' % (u['key'], '／'.join(u['labs']), d))
        L.append('')
    if disorder:
        L += ['## 同卷 raw_start 非單調（前 50）', '',
              '| key | vol | raw_start |', '|:--|:--|--:|']
        for u in disorder[:50]:
            L.append('| %s | %s | %s |' % (u['key'], u['vol'], u['raw_start']))
        L.append('')
    io.open(os.path.join(outdir, '_原文核驗.md'), 'w', encoding='utf-8').write(
        '\n'.join(L))


# ---------------------------------------------------------------- 主流程
def generate(book, outdir, target, mode, gap_mode, gap_min, check_raw,
             limit=0, dry_run=False, force=False, group_by='vol', verbose=True):
    raws = load_raw(book)
    raw_h = raws[0]
    order = make_units(book, raw_h)
    for i, u in enumerate(order):
        u['prev_key'] = order[i - 1]['key'] if i > 0 else ''
        u['next_key'] = order[i + 1]['key'] if i + 1 < len(order) else ''
    disorder = [u for u in order if not u.get('mono')]
    gap_detect = (len(disorder) <= max(20, int(len(order) * 0.05)))
    effective_gap_mode = gap_mode if gap_detect else 'off'
    if gap_mode != 'off' and not gap_detect and verbose:
        print('  ⚠ %s raw_start 同卷順序可疑 %d／%d 筆（>5%%），'
              '依 gap 切檔會切出假缺口；本輪改用 gap-mode=off。'
              % (book, len(disorder), len(order)))
    packs = build_packs(book, order, target, mode, effective_gap_mode,
                        gap_min, raw_h, group_by)
    if limit:
        packs = packs[:limit]
    stats = {
        'book': book, 'book_id': BOOKS[book]['id'],
        'target_chars': target, 'count_mode': mode, 'group_by': group_by,
        'gap_mode': effective_gap_mode, 'gap_detect': gap_detect,
        'units': len(order), 'packs': len(packs),
        'chars': sum(unit_size(u, 'body') for u in order),
        'dirty': len([u for u in order if u.get('dirty')]),
        'raw': bool(raw_h), 'raw_path': raws[1],
    }
    if verbose:
        print('%s：定稿 %s 單位，打包 %d 檔（%s，約 %s 字%s）'
              % (book, _fmt(len(order)), len(packs),
                 '整份 md' if mode == 'md' else ('原文＋現譯' if mode == 'body' else '僅原文'),
                 _fmt(target), '；不跨 %s' % group_by))
    if dry_run:
        _sizes = [sum(unit_size(u, 'body') for u in p) for p in packs]
        _md = None
        if mode == 'md':
            _md = []
            for p in packs:
                _md.append(_render_len(book, p, order, effective_gap_mode,
                                       gap_min, raw_h, mode))
            print('  md 字數：最小 %s／中位 %s／最大 %s；19K–20.5K 外 %d 檔'
                  % (_fmt(min(_md)), _fmt(sorted(_md)[len(_md) // 2]),
                     _fmt(max(_md)),
                     sum(1 for x in _md if x < 19000 or x > 20500)))
        print('  待審（原文＋現譯）字數：最小 %s／中位 %s／最大 %s'
              % (_fmt(min(_sizes)), _fmt(sorted(_sizes)[len(_sizes) // 2]),
                 _fmt(max(_sizes))))
        if check_raw:
            if raw_h is None:
                print('  原文核驗：底本不可用（%s 無對應原文檔），raw 驗證 unavailable'
                      % book)
            else:
                bad_units = [u for u in order if u.get('raw_ok') is False]
                bad_parts = [(u, p) for u in order for p in u['parts']
                             if p.get('raw_ok') is False]
                joined_bad = [u for u in order if u.get('parts_joined') is False]
                print('  原文核驗：底本 %s；source 不符 %d；parts 拼接不符 %d；'
                      'part 定位不符 %d；順序可疑 %d'
                      % (raws[1] or '（無）', len(bad_units), len(joined_bad),
                         len(bad_parts), len(disorder)))
        return stats
    os.makedirs(outdir, exist_ok=True)
    rep = os.path.join(outdir, '回覆')
    if os.path.isdir(rep) and any(f.endswith('_回.txt') for f in os.listdir(rep)) \
            and not force:
        raise SystemExit('（已中止）輸出目錄已有回覆，重產材料會造成資料錯位：%s\n'
                         '  確定重跑請加 --force，或改用新目錄。' % outdir)
    existing = [f for f in os.listdir(outdir)
                if re.match(r'.*_r\d{4}\.(md|json)$', f)]
    if existing and not force:
        raise SystemExit('（已中止）輸出目錄已有再審材料（%d 個），'
                         '請加 --force 或換目錄：%s' % (len(existing), outdir))
    for f in list(os.listdir(outdir)):
        if re.match(r'.*_r\d{4}\.(md|json)$', f) or f in ('索引.json', '_原文核驗.md'):
            try:
                os.remove(os.path.join(outdir, f))
            except OSError:
                pass
    meta_all = []
    _pos = {u['key']: j for j, u in enumerate(order)}
    for i, pack in enumerate(packs, 1):
        i0 = order.index(pack[0])
        i1 = order.index(pack[-1])
        pre = context_before(order, i0)
        post = context_after(order, i1)
        gaps = _pack_gaps(pack, order, effective_gap_mode, gap_min, raw_h)
        # 全書 pack 也要掛對照層：逐 unit 收集、去重、總長 ≤2800
        pack_refs, seen_ref, ref_len = [], set(), 0
        for u in pack:
            for title, body in reference_blocks(book, u, order, _pos[u['key']]):
                if not (body or '').strip():
                    continue
                sig = re.sub(r'\s+', '', body)[:80]
                if sig in seen_ref:
                    continue
                if ref_len + len(body) > 2800:
                    continue
                seen_ref.add(sig)
                pack_refs.append((title, body))
                ref_len += len(body)
        key, meta = emit_pack(outdir, pack, i, book, BOOKS[book]['id'], mode,
                              gaps, raw_h, pre=pre, post=post, target=target,
                              refs=pack_refs)
        meta['n_units'] = len(pack)
        meta_all.append(meta)
    json.dump({
        'book': book, 'book_id': BOOKS[book]['id'], 'target_chars': target,
        'count_mode': mode, 'group_by': group_by,
        'gap_mode': effective_gap_mode, 'generated': _now(), 'stats': stats,
        'packs': [{k: m[k] for k in ('key', 'vol', 'chunk', 'n_units', 'raw_start',
                                     'raw_end', 'chars', 'md_chars', 'hash')}
                  for m in meta_all],
    }, io.open(os.path.join(outdir, '索引_%s.json' % bid), 'w', encoding='utf-8'),
        ensure_ascii=False, indent=1)
    if check_raw:
        bad_units = [u for u in order if u.get('raw_ok') is False]
        bad_parts = [(u, p) for u in order for p in u['parts']
                     if p.get('raw_ok') is False]
        _write_raw_check(outdir, book, raws, order, bad_units, bad_parts,
                         disorder, raws[1])
        if raw_h is None:
            print('  原文核驗：底本不可用，raw 驗證 unavailable → _原文核驗.md')
        else:
            joined_bad = [u for u in order if u.get('parts_joined') is False]
            print('  原文核驗：source 不符 %d、parts 拼接不符 %d、part 定位不符 %d、'
                  '順序可疑 %d → _原文核驗.md'
                  % (len(bad_units), len(joined_bad), len(bad_parts), len(disorder)))
    print('已產生 %d 檔 → %s' % (len(meta_all), os.path.relpath(outdir, B)))
    if mode == 'md':
        _over = [m['key'] for m in meta_all if m['md_chars'] > target * MD_TOL + 1]
        if _over:
            print('  ⚠ 有 %d 檔 md 超過 %s 字（多為單一超長 unit，無法再切）：%s'
                  % (len(_over), _fmt(int(target * MD_TOL)),
                     '、'.join(_over[:8])))
    if meta_all:
        _md = [m['md_chars'] for m in meta_all]
        _body = [m['chars']['total'] for m in meta_all]
        print('  md 字數：最小 %s／中位 %s／最大 %s'
              % (_fmt(min(_md)), _fmt(sorted(_md)[len(_md) // 2]), _fmt(max(_md))))
        print('  待審字數：最小 %s／中位 %s／最大 %s'
              % (_fmt(min(_body)), _fmt(sorted(_body)[len(_body) // 2]),
                 _fmt(max(_body))))
        print('  首檔 %s（%s，%d 單位，md %s 字）'
              % (meta_all[0]['key'], meta_all[0]['vol'], meta_all[0]['n_units'],
                 _fmt(meta_all[0]['md_chars'])))
    return stats


def main():
    ap = argparse.ArgumentParser(
        description='從 定稿/<book>.jsonl 打包約 20K 字的再審材料（不呼叫 qwen）')
    ap.add_argument('--book', default='業疏', choices=list(BOOKS), help='書別（預設 業疏）')
    ap.add_argument('--target-chars', type=int, default=TARGET_CHARS,
                    help='每檔目標字數（預設 10000；全量建議 9000–10000）')
    ap.add_argument('--count-mode', default='md', choices=COUNT_MODES,
                    help='字數計法：md＝整份材料（預設）、body＝原文＋現譯、source＝僅原文')
    ap.add_argument('--group-by', default='vol', choices=GROUP_BY,
                    help='不跨的層級：vol＝卷（預設）、chunk＝分卷 chunk')
    ap.add_argument('--out', default='',
                    help='輸出目錄（預設 測試/重譯/<book>/_再審；--dry-run 可省略）')
    ap.add_argument('--check-raw', action='store_true',
                    help='逐單位驗證 source 與底本 raw 區間，並出 _原文核驗.md')
    ap.add_argument('--gap-mode', default='cut', choices=('cut', 'note', 'off'),
                    help='正文缺口處理：cut＝切檔（預設）、note＝加禁止代譯提示、off＝不處理')
    ap.add_argument('--gap-min', type=int, default=GAP_MIN,
                    help='缺口判定門檻（漢字，預設 20）')
    ap.add_argument('--limit', type=int, default=0, help='只輸出前 N 檔（試跑用）')
    ap.add_argument('--dry-run', action='store_true', help='只統計，不寫任何檔案')
    ap.add_argument('--force', action='store_true', help='允許覆寫既有材料')
    ap.add_argument('--single', action='store_true',
                    help='單段模式：每個 key 一份 .md／.json（回歸 50 用）')
    ap.add_argument('--keys-file', default='',
                    help='單段模式的 key 清單 JSON：{"書別":["key",…]}')
    ap.add_argument('--pre-cap', type=int, default=PRE_SRC_CAP,
                    help='前文原文上限（單段模式預設 1500；v2 回歸用 1800）')
    ap.add_argument('--post-cap', type=int, default=POST_SRC_CAP,
                    help='後文原文上限（單段模式預設 600）')
    args = ap.parse_args()
    outdir = (_resolve_path(args.out) if args.out
              else os.path.join(B, default_out(args.book).replace('/', os.sep)))
    if not args.out and not args.dry_run:
        print('（未指定 --out，使用預設：%s）' % default_out(args.book))
    if args.single:
        if not args.keys_file:
            raise SystemExit('--single 需同時給 --keys-file')
        spec = json.load(io.open(_resolve_path(args.keys_file), encoding='utf-8'))
        keys = spec.get(args.book) or []
        if isinstance(keys, dict):
            keys = keys.get('keys') or []
        if not keys:
            raise SystemExit('--keys-file 內沒有《%s》的 key' % args.book)
        if args.dry_run:
            print('%s：%d 個 key；--dry-run 不寫檔' % (args.book, len(keys)))
            return
        generate_single(args.book, outdir, keys, pre_cap=args.pre_cap,
                        post_cap=args.post_cap, check_raw=args.check_raw,
                        force=args.force)
        return
    generate(args.book, outdir, args.target_chars, args.count_mode,
             args.gap_mode, args.gap_min, args.check_raw, args.limit,
             args.dry_run, args.force, args.group_by)


def _resolve_path(p):
    p = p.replace('/', os.sep)
    return p if os.path.isabs(p) else os.path.join(B, p)


if __name__ == '__main__':
    main()
