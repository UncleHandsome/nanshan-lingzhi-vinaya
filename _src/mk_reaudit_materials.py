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

TARGET_CHARS = 20000
COUNT_MODES = ('md', 'body', 'source')
GROUP_BY = ('vol', 'chunk')
PRE_SRC_CAP = 1500
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

RA_PROMPT = (
    '你是南山律典 20K 再審校閱員，對照【原文】逐段核對【現譯】，只抓實質錯誤。\n\n'
    '### 範圍與讀法\n'
    '1. 本檔含多個獨立單位，每單位以 `### [編號]（key: …）` 起始，其下交錯'
    '`■ 段別（原文）[編號]` 與 `■ 段別（現譯）[編號]`；逐單位獨立核對，'
    '不得跨單位合併、改寫、重排或增刪單位。\n'
    '2. 先遮蔽【現譯】單讀【原文】，獨立拆解文法、主客施受、條件界限與律義，再反向驗收【現譯】，'
    '切勿順著譯文流暢度讀過；已發現硬傷仍須核完其餘單位。\n'
    '3. 【前文背景】【後文背景】僅供銜接理解，嚴禁譯入正文；背景或段間若見【正文缺口提示】，'
    '該缺口係定稿未收錄之正文，禁止代譯、補譯或憑上下文虛構，亦不得據此判現譯漏譯。\n'
    '4. {book_note}\n'
    '5. 只改實質錯誤、硬性語病及違反【全書體例與格式規範】之處（不挑純修辭）：\n'
    '{logic_checklist}\n'
    '6. 不判 FIX：純換詞潤飾；簡繁／異體字、戒名引號、典籍簡稱展開等純表面格式；'
    '依體例保留之被訓釋原詞、專名、儀軌稱謂「某甲」、度量、「某某反」與未定校勘〔…〕；'
    '合乎原文脈絡之簡短消歧括注。\n\n'
    '{style_spec}\n\n'
    '### 輸出（勿改寫整段、勿代寫完整替換句、勿輸出前言）\n'
    '【分段核驗表】\n'
    '[01] 通過\n'
    '[02] 通過\n'
    '[03] 硬傷 1 項\n'
    '……（每個單位一行，編號自 [01] 起連續到本檔最後一號，不得跳號、不得合併、不得省略；'
    '本表須完整涵蓋本檔全部單位，缺一號即視為回覆失敗。）\n\n'
    '【必改硬傷】\n'
    '- 無硬傷只寫「無」一字，勿寫「經核對…」等說明。\n'
    '- 有硬傷每項一行，行首必須標明所屬單位編號（如 `[03]`），未經點名之單位視為 PASS：\n'
    '  `[03] 【疏文】原文「……」→ 現譯「……」｜問題：……｜依據：……｜修正方向：……`\n'
    '- 同一單位多項硬傷，每項都重寫該編號，勿用「同上」或省略編號；'
    '修正方向只寫須補齊或糾正之要素，勿照抄半文半白用詞。\n'
    '- 依據欄須引原文或書名卷次；外部查證須摘錄關鍵原句 1–2 句；無據不得強令猜補。\n'
)

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
    segs = row.get('segments') or []
    parts = []
    for s in segs:
        lab = s.get('label') or row.get('label') or '鈔文'
        orig = (s.get('source') or '').strip()
        tr = _LAB_HEAD.sub('', (s.get('translation') or '').strip())
        if not orig and not tr:
            continue
        parts.append({'lab': lab, 'orig': orig, 'tr': tr})
    if not parts:
        lab = row.get('label') or '鈔文'
        orig = (row.get('source') or '').strip()
        tr = _LAB_HEAD.sub('', (row.get('translation') or '').strip())
        parts.append({'lab': lab, 'orig': orig, 'tr': tr})
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


def context_before(order, i0):
    u0 = order[i0]
    src, tr = '', ''
    if i0 > 0 and order[i0 - 1]['vol'] == u0['vol']:
        tr = _clip_tail(order[i0 - 1]['parts'][-1]['tr'], PRE_TR_CAP)
        buf, acc = [], 0
        for j in range(i0 - 1, -1, -1):
            if order[j]['vol'] != u0['vol']:
                break
            t = '\n'.join(p['orig'] for p in order[j]['parts'])
            buf.append(t)
            acc += len(han(t))
            if acc >= PRE_SRC_CAP:
                break
        src = _clip_tail('\n'.join(reversed(buf)), PRE_SRC_CAP)
    return src, tr


def context_after(order, i1):
    u1 = order[i1]
    src, tr = '', ''
    if i1 + 1 < len(order) and order[i1 + 1]['vol'] == u1['vol']:
        tr = _clip_head(order[i1 + 1]['parts'][0]['tr'], POST_TR_CAP)
        buf, acc = [], 0
        for j in range(i1 + 1, len(order)):
            if order[j]['vol'] != u1['vol']:
                break
            t = '\n'.join(p['orig'] for p in order[j]['parts'])
            buf.append(t)
            acc += len(han(t))
            if acc >= POST_SRC_CAP:
                break
        src = _clip_head('\n'.join(buf), POST_SRC_CAP)
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


def render_material(book, pack, idx, book_id, key, pre, post, gaps, mode, raws,
                    mother=''):
    vol = pack[0]['vol'] or '（未分卷）'
    n = len(pack)
    src_chars = sum(len(p['orig']) for u in pack for p in u['parts'])
    tr_chars = sum(len(p['tr']) for u in pack for p in u['parts'])
    labs = sorted({p['lab'] for u in pack for p in u['parts']})
    dual = book in ('業疏', '戒疏') and {'疏文', '記文'} <= set(labs)
    note = BC.note_for(book, labs)
    if dual:
        note += ('\n此兩欄同屬一個單位，須雙向互核：【疏文】與【記文】之科判、釋義、'
                 '列舉項數與施受主語須前後相契，並確認【疏文】未隱沒【記文】所牒實詞；'
                 '【疏文】為消歧、還原指代或補全必要量詞之極簡實指不判 FIX。')
    prompt = (RA_PROMPT.replace('{book_note}', note)
              .replace('{logic_checklist}', BC.LOGIC_CHECKLIST)
              .replace('{style_spec}', BC.STYLE_SPEC))
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
              pre=None, post=None, parent='', part='', key='', target=TARGET_CHARS):
    key = key or '%s_r%04d' % (book_id, idx)
    pre = pre if pre is not None else ('', '')
    post = post if post is not None else ('', '')
    mother = mother_text(pack, book)
    md = render_material(book, pack, idx, book_id, key, pre, post, gaps, mode,
                         raws, mother)
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
        'parent': parent, 'part': part,
        'units': units_json,
        'hash': _h12('|'.join(u['hash'] for u in pack)),
    }
    io.open(os.path.join(outdir, key + '.json'), 'w', encoding='utf-8').write(
        json.dumps(meta, ensure_ascii=False, indent=1))
    return key, meta


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
    for i, pack in enumerate(packs, 1):
        i0 = order.index(pack[0])
        i1 = order.index(pack[-1])
        pre = context_before(order, i0)
        post = context_after(order, i1)
        gaps = _pack_gaps(pack, order, effective_gap_mode, gap_min, raw_h)
        key, meta = emit_pack(outdir, pack, i, book, BOOKS[book]['id'], mode,
                              gaps, raw_h, pre=pre, post=post, target=target)
        meta['n_units'] = len(pack)
        meta_all.append(meta)
    json.dump({
        'book': book, 'book_id': BOOKS[book]['id'], 'target_chars': target,
        'count_mode': mode, 'group_by': group_by,
        'gap_mode': effective_gap_mode, 'generated': _now(), 'stats': stats,
        'packs': [{k: m[k] for k in ('key', 'vol', 'chunk', 'n_units', 'raw_start',
                                     'raw_end', 'chars', 'md_chars', 'hash')}
                  for m in meta_all],
    }, io.open(os.path.join(outdir, '索引.json'), 'w', encoding='utf-8'),
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
                    help='每檔目標字數（預設 20000；預設計整份 md）')
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
    args = ap.parse_args()
    outdir = (_resolve_path(args.out) if args.out
              else os.path.join(B, default_out(args.book).replace('/', os.sep)))
    if not args.out and not args.dry_run:
        print('（未指定 --out，使用預設：%s）' % default_out(args.book))
    generate(args.book, outdir, args.target_chars, args.count_mode,
             args.gap_mode, args.gap_min, args.check_raw, args.limit,
             args.dry_run, args.force, args.group_by)


def _resolve_path(p):
    p = p.replace('/', os.sep)
    return p if os.path.isabs(p) else os.path.join(B, p)


if __name__ == '__main__':
    main()
