# -*- coding: utf-8 -*-
"""本地索引擴充：加入南山著作（業疏／戒疏／行事鈔／資持記／尼鈔）。"""
import io
import json
import os
import re
import threading
from glob import glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
YUAN = os.path.join(B, '原文')
TXT = os.path.join(B, 'TXT')

BOOKS = ['四分律', '五分律', '十誦律', '摩訶僧祇律', '善見律毘婆沙', '律二十二明了論', '隨機羯磨', '戒疏科', '行宗記', '業疏科', '濟緣記', '行事鈔科', '義鈔科', '尼鈔科', '薩婆多毘尼毘婆沙',
         '成實論','大般涅槃經','優婆塞戒經','雜阿毘曇心論','增壹阿含經','大比丘三千威儀','關中創立戒壇圖經','四分比丘尼戒本','梵網經','瑜伽師地論', '毘尼母經', '根本說一切有部律', '含注戒本', '行事鈔批','薩婆多部毘尼摩得勒伽', '南山律學辭典']

# 南山著作（自家會本／記文），用於查平行文與用語
EXTRA = {
    '業疏': [os.path.join(TXT, '03_四分律刪補隨機羯磨疏.txt')],
    '戒疏': [os.path.join(TXT, '02_四分律含注戒本疏.txt')],
    '行事鈔': [os.path.join(TXT, '01_四分律刪繁補闕行事鈔.txt')],
    '義鈔': [os.path.join(TXT, '05_四分律拾毗尼義鈔.txt')],
    '尼鈔': [os.path.join(TXT, '04_四分律比丘尼鈔.txt')],
    '資持記': sorted(glob(os.path.join(TXT, '資持記', '*.txt'))),
}

PUNCT_RE = re.compile(r"[^\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaffA-Za-z0-9]")


_VAR_MAP = str.maketrans('煑竪虗汙竝説爲於着衆盋鉢艸壍婬呪眞敎菓覩羣牀裏徧却麤廻敍祕衞弃処体无証堕徳毗鶴玅葢冐輭徤帀墻鬬襵㭊',
                         '煮豎虛污並說為于著眾缽缽草塹淫咒真教果睹群床裡遍卻粗迴敘秘衛棄處體無證墮德毘鶴妙蓋冒軟健匝牆鬥攝析')

# 底本用字與通行字之整詞對應（先於逐字轉換）
_PRE_MAP = (('窯治', '窯冶'),)

# 尼鈔校閱時，直引母律優先於《辭典》《資持記》
NICAO_MOTHER = ('四分律', '摩訶僧祇律', '五分律', '十誦律', '毘尼母經', '四分比丘尼戒本')

# 各書校閱時，鄰近書（同層優先、每書多給 1 名額）
CTX_MORE = {
    '資持記': {'行事鈔', '業疏'},
    '業疏': {'隨機羯磨', '四分律'},
    '戒疏': {'含注戒本', '四分律'},
    '尼鈔': set(NICAO_MOTHER),
    # 《義鈔輔要記》目前 原文/ 書庫未收，僅保留介面；有檔案時自動生效
    '義鈔': {'義鈔輔要記', '戒疏', '行宗記', '資持記', '行事鈔'},
}


def _plain(s):
    s = str(s)
    for _a, _b in _PRE_MAP:
        s = s.replace(_a, _b)
    # 先轉異體字再過濾標點：避免相容區罕見字（如 U+FA2D／增補區字）被當標點洗掉
    return PUNCT_RE.sub("", s.translate(_VAR_MAP))


ALIASES = [
    ('雜心', '雜阿毘曇心論'),
    ('四分律比丘尼戒本', '四分比丘尼戒本'),
    ('拾毗尼義鈔', '義鈔'),
    ('四分律含注戒本', '含注戒本'), ('毘尼母經', '毘尼母經'), ('母經', '毘尼母經'), ('含注戒本', '含注戒本'), ('四分律行事鈔批', '行事鈔批'), ('行事鈔批', '行事鈔批'), ('四分律比丘含注戒本', '含注戒本'),
    ('四分律刪繁補闕行事鈔科', '行事鈔科'),
    ('四分律拾毗尼義鈔', '義鈔'),
    ('四分律隨機羯磨', '隨機羯磨'),
    ('四分律刪補隨機羯磨疏', '業疏'),
    ('隨機羯磨疏濟緣記', '濟緣記'),
    ('含注戒本疏行宗記', '行宗記'),
    ('四分律刪補隨機羯磨疏濟緣記', '濟緣記'),
    ('尼戒本', '四分比丘尼戒本'),
    ('三千威儀', '大比丘三千威儀'),
    ('戒壇圖經', '關中創立戒壇圖經'),
    ('瑜伽論', '瑜伽師地論'), ('母論', '毘尼母經'),
    ('雜心論', '雜阿毘曇心論'),
    ('成論', '成實論'),
    ('涅槃經', '大般涅槃經'),
    ('善生', '優婆塞戒經'),
    ('善生經', '優婆塞戒經'),
    ('四分律行事鈔科', '行事鈔科'),
    ('四分律比丘尼鈔科', '尼鈔科'),
    ('四分律含注戒本疏科', '戒疏科'),
    ('四分律含戒本疏科', '戒疏科'),
    ('四分律含注戒本疏行宗記', '行宗記'),
    ('四分律刪補隨機羯磨疏科', '業疏科'),

    ('四分律刪繁補闕行事鈔資持記', '資持記'),
    ('四分律行事鈔資持記', '資持記'),
    ('行事鈔資持記', '資持記'),
    ('四分律刪繁補闕行事鈔', '行事鈔'),
    ('四分律行事鈔', '行事鈔'),
    ('四分律刪補隨機羯磨疏濟緣記', '濟緣記'),
    ('四分律隨機羯磨疏', '業疏'),
    ('隨機羯磨疏', '業疏'),
    ('羯磨疏', '業疏'),
    ('四分律含注戒本疏', '戒疏'),
    ('含注戒本疏', '戒疏'),
    ('四分律比丘尼鈔', '尼鈔'),
    ('比丘尼鈔', '尼鈔'),
    ('善見律毘婆沙', '善見律毘婆沙'),
    ('伽論', '薩婆多部毘尼摩得勒伽'),
    ('摩得勒伽', '薩婆多部毘尼摩得勒伽'),
    ('婆沙', '薩婆多毘尼毘婆沙'),
    ('婆論', '薩婆多毘尼毘婆沙'),
    ('多論', '薩婆多毘尼毘婆沙'),
    ('薩婆多論', '薩婆多毘尼毘婆沙'),
    ('摩得勒伽論', '薩婆多部毘尼摩得勒伽'),
    ('根本有部律', '根本說一切有部律'),
    ('有部律', '根本說一切有部律'),
    ('明了論', '律二十二明了論'),
    ('善見律', '善見律毘婆沙'),
    ('善見', '善見律毘婆沙'),
    ('辭典', '南山律學辭典'),
    ('南山辭典', '南山律學辭典'),
    ('見論', '善見律毘婆沙'),
    ('四分', '四分律'),
    ('五分', '五分律'),
    ('十誦', '十誦律'),
    ('僧祇', '摩訶僧祇律'),
    ('僧祇律', '摩訶僧祇律'),
    ('三千威儀經', '大比丘三千威儀'),
]



def _norm_book(s):
    """書名正規化：先精確比對，再剝《》與空白並套 ALIASES。"""
    q = str(s).strip().strip('《》〈〉「」『』 ')
    if q in KNOWN_BOOKS:
        return q
    for alias, target in sorted(ALIASES, key=lambda x: len(x[0]), reverse=True):
        if q == alias:
            return target
    for nm in sorted(KNOWN_BOOKS, key=len, reverse=True):
        if q.startswith(nm):
            return nm
    return q


def _norm_query(s):
    return str(s).replace('《', '').replace('》', '').strip()


_CITE_WORDS = {'善見', '四分', '成論', '婆沙', '多論', '母論', '雜心', '伽論',
               '涅槃', '瑜伽', '十誦', '五分', '僧祇'}


def _split_work(query):
    """查詢若以書名（含別名）開頭，拆成 (work, 核心詞)。"""
    names = set(BOOKS) | set(EXTRA.keys()) | set(a for a, _ in ALIASES)
    q = _norm_query(query)
    parts = q.split()
    if len(parts) >= 2 and parts[0] in names and parts[0] not in _CITE_WORDS:
        return dict(ALIASES).get(parts[0], parts[0]), ' '.join(parts[1:])
    for nm in sorted(names, key=len, reverse=True):
        if nm in _CITE_WORDS:
            continue
        if q.startswith(nm) and len(q) > len(nm) + 1 and q[len(nm)] in ' 　:：':
            _rest = q[len(nm):].strip()
            if _rest.startswith(tuple(names)):
                return None, q
            return dict(ALIASES).get(nm, nm), _rest
    return None, q


JUAN_RE = re.compile(r'卷[第]?[上中下]?(?:之[上中下\d一二三四五六七八九十]{1,3})?[一二三四五六七八九十百千零〇\d]{0,3}')
HAN = re.compile(r'[\u4e00-\u9fff]')

KNOWN_BOOKS = set(BOOKS) | set(EXTRA.keys())

_LOAD_LOCK = threading.Lock()

BOOK_BLOB = {}
LINES = []
BOOK_LINES = {}

_LOADED = False



def _orig_index(text, plain_pos):
    """把去標點字串的位置映射回原行索引。"""
    cnt = 0
    for idx, ch in enumerate(text):
        if PUNCT_RE.match(ch):
            continue
        if cnt == plain_pos:
            return idx
        cnt += 1
    return max(0, len(text) - 1)


def _juan_label(line, book):
    s = line.strip()
    if len(s) > 24 or re.search(r'[。！？，、；：]', s) or s.startswith(('如', '見', '若')):
        return None
    m = JUAN_RE.search(s)
    if not m or len(s) > 40 or s.startswith(('如', '見', '若')):
        return None
    v = m.group(0)
    if v in ('卷', '卷第'):
        return None
    return v


def _add_file(path, book, juan_default='卷首'):
    juan = juan_default
    try:
        raw = io.open(path, encoding='utf-8', errors='ignore').read()
    except Exception:
        return
    for i, line in enumerate(raw.split('\n')):
        s = line.strip()
        if not s:
            continue
        m = JUAN_RE.search(s)
        _pure = (not re.search(r'[。！？，、；：]', s)) and len(s) <= 40
        if m and _pure and not s.startswith(('如', '見', '若')):
            _v = m.group(0)
            if _v not in ('卷', '卷第'):
                juan = _v
                continue
        if not HAN.search(s):
            continue
        rec = {'id': '%s|%s|%d' % (book, os.path.basename(path), i), 'book': book,
               'juan': juan, 'no': i, 'text': s, 'plain': _plain(s)}
        BOOK_LINES.setdefault(book, []).append(len(LINES))
        LINES.append(rec)


def load():
    global _LOADED
    with _LOAD_LOCK:
        if _LOADED:
            return LINES
        priority = ['南山律學辭典', '濟緣記', '行宗記', '業疏科', '戒疏科',
                    '隨機羯磨', '四分律', '善見律毘婆沙', '律二十二明了論']
        order = [b for b in priority if b in BOOKS] + [b for b in BOOKS if b not in priority]
        for book in order:
            d = os.path.join(YUAN, book)
            if not os.path.isdir(d):
                continue
            juan = '卷第一'
            for fn in sorted(os.listdir(d)):
                if not fn.endswith('.txt'):
                    continue
                try:
                    raw = io.open(os.path.join(d, fn), encoding='utf-8', errors='ignore').read()
                except Exception:
                    continue
                for i, line in enumerate(raw.split('\n')):
                    s = line.strip()
                    if not s:
                        continue
                    lab = _juan_label(s, book)
                    if lab and (re.search(r'[。！？，、；：]', s) or s.startswith(('如', '見', '若'))):
                        lab = None
                    if lab:
                        juan = lab
                        continue
                    if not HAN.search(s):
                        continue
                    rec = {'id': '%s|%s|%d' % (book, fn, i), 'book': book,
                           'juan': juan, 'no': i, 'text': s, 'plain': _plain(s)}
                    BOOK_LINES.setdefault(book, []).append(len(LINES))
                    LINES.append(rec)
        for book, paths in EXTRA.items():
            for p in paths:
                _add_file(p, book)
        import collections as _c
        _tmp = _c.defaultdict(list)
        for _r in LINES:
            _tmp[_r['book']].append(_r['plain'])
        for _b, _ls in _tmp.items():
            BOOK_BLOB[_b] = ''.join(_ls)
        _LOADED = True
        return LINES


def find(query, work=None, limit=6, pad=240, per_book=None, ctx_book=None):

    """全庫掃描後分層取樣：科記／辭典 → 南山正文 → 律藏，並回傳各書命中數。

    ctx_book＝目前校閱的書；《資持記》查短詞時保證 1 個《行事鈔》名額。
    """
    load()
    auto_work, core = _split_work(query)
    if auto_work and not work:
        work = auto_work
    if work:
        work = _norm_book(work)
    core = _norm_query(core)
    _boost = (not work and ctx_book == '資持記')
    terms = [_plain(t) for t in str(core).split()]
    terms = [t for t in terms if len(t) >= 2]
    if not terms:
        qp = _plain(str(core).strip())
        if not qp:
            return []
        terms = [qp]

    terms_sorted = sorted(terms, key=len, reverse=True)
    anchor, others = terms_sorted[0], terms_sorted[1:]
    hits = []
    if per_book is None:
        per_book = limit if work else 1
    counts = {}
    _seen = {}
    _blob = {b: s for b, s in BOOK_BLOB.items()
             if not work or (b == work if str(work) in KNOWN_BOOKS else str(work) in b)}
    _blob = {b: s for b, s in _blob.items() if anchor in s}
    if work and work in BOOK_LINES:
        _idxs = BOOK_LINES[work]
    else:
        _idxs = [i for _b in _blob for i in BOOK_LINES.get(_b, [])]
        _idxs.sort()
    for idx in _idxs:
        r = LINES[idx]
        if work:
            if str(work) in KNOWN_BOOKS:
                if r['book'] != str(work):
                    continue
            elif str(work) not in r['book']:
                continue
        if r['book'] not in _blob:
            continue
        eidx = idx
        if anchor not in r.get('plain', r['text']):
            _ok = False
            for _off in (1, 2):
                _j = idx + _off
                if _j < len(LINES) and LINES[_j]['book'] == r['book']:
                    if anchor in LINES[_j].get('plain', ''):
                        eidx = _j       # 命中落在後 1–2 行：歸給該行，避免本行搶走
                        _ok = True
                        break
                    if anchor in ''.join(LINES[x].get('plain', '') for x in range(idx, _j + 1)
                                         if LINES[x]['book'] == r['book']):
                        _ok = True
                        break
            if not _ok:
                continue
        r = LINES[eidx]
        if others:
            # 依實際字數湊足前後各 240 字，不鎖行數
            lo_i, hi_i = eidx, eidx + 1
            _acc = len(r.get('plain', r['text']))
            while lo_i > 0 and _acc < 240 * 2:
                _j = lo_i - 1
                if LINES[_j]['book'] != r['book']:
                    break
                lo_i = _j
                _acc += len(LINES[_j].get('plain', LINES[_j]['text']))
            _acc = len(r.get('plain', r['text']))
            while hi_i < len(LINES) and _acc < 240 * 2:
                if LINES[hi_i]['book'] != r['book']:
                    break
                _acc += len(LINES[hi_i].get('plain', LINES[hi_i]['text']))
                hi_i += 1
            win = ''.join(LINES[j].get('plain', LINES[j]['text'])
                          for j in range(lo_i, hi_i) if LINES[j]['book'] == r['book'])
            if not all(t in win for t in others):
                continue
        _last = _seen.get(r['book'])
        if _last is not None and eidx - _last <= 2:
            continue
        _seen[r['book']] = eidx
        counts[r['book']] = counts.get(r['book'], 0) + 1
        hits.append((eidx, r))

    layer = {'南山律學辭典': 0, '濟緣記': 0, '行宗記': 0, '業疏科': 0, '戒疏科': 0, '行事鈔科': 0, '義鈔科': 0, '尼鈔科': 0,
             '行事鈔': 1, '業疏': 1, '戒疏': 1, '資持記': 1, '尼鈔': 1, '隨機羯磨': 1,
             '四分律': 2, '五分律': 2, '十誦律': 2, '摩訶僧祇律': 2,
             '根本說一切有部律': 2, '薩婆多毘尼毘婆沙': 2, '薩婆多部毘尼摩得勒伽': 2, '善見律毘婆沙': 2, '律二十二明了論': 2, '義鈔': 1,
             '成實論': 2, '大般涅槃經': 2, '優婆塞戒經': 2, '雜阿毘曇心論': 2,
             '增壹阿含經': 2, '大比丘三千威儀': 2, '關中創立戒壇圖經': 2,
             '四分比丘尼戒本': 2, '梵網經': 2, '瑜伽師地論': 2, '毘尼母經': 2,
             '行事鈔批': 0, '含注戒本': 1}
    if ctx_book == '尼鈔':
        # 尼鈔：直引母律（四分／僧祇／五分／十誦／母論）優先於辭典與資持記
        for _b in NICAO_MOTHER:
            layer[_b] = 0
        layer['南山律學辭典'] = 1
        layer['資持記'] = 1
        layer['行事鈔'] = 1
    _ctx_more = CTX_MORE.get(ctx_book or '', set())
    hits.sort(key=lambda x: (
        layer.get(x[1]['book'], 3),
        0 if (not work and (x[1]['book'] == ctx_book or x[1]['book'] in _ctx_more)) else 1,
        x[0]))

    # 分層配額：每層最多取 2 筆，保證律藏也看得到
    by_layer = {}
    for item in hits:
        by_layer.setdefault(layer.get(item[1]['book'], 3), []).append(item)
    ordered = []
    for round_i in range(3):
        for lv in sorted(by_layer):
            if len(by_layer[lv]) > round_i:
                ordered.append(by_layer[lv][round_i])
    _seen = {h[1]['id'] for h in ordered if isinstance(h[1], dict) and 'id' in h[1]}
    for h in hits:
        _hid = h[1].get('id') if isinstance(h[1], dict) else None
        if _hid in _seen:
            continue
        _seen.add(_hid)
        ordered.append(h)

    out = []
    used = {}
    for idx, r in ordered:
        _ctx_more = CTX_MORE.get(ctx_book or '', set())
        _pb = 2 if (ctx_book and not work and
                    (r['book'] == ctx_book or r['book'] in _ctx_more)) else per_book
        if used.get(r['book'], 0) >= _pb:
            continue
        used[r['book']] = used.get(r['book'], 0) + 1
        lo_i, hi_i = idx, idx + 1
        _acc = len(_plain(LINES[idx]['text']))
        while lo_i > 0 and _acc < 480:
            if LINES[lo_i - 1]['book'] != r['book']:
                break
            lo_i -= 1
            _acc += len(_plain(LINES[lo_i]['text']))
        _acc = len(_plain(LINES[idx]['text']))
        while hi_i < len(LINES) and _acc < 480:
            if LINES[hi_i]['book'] != r['book']:
                break
            _acc += len(_plain(LINES[hi_i]['text']))
            hi_i += 1
        ctx = '\n'.join(LINES[j]['text'] for j in range(lo_i, hi_i)
                         if LINES[j]['book'] == r['book'])
        _pos_line = _plain(r['text']).find(anchor)
        _needle = _plain(r['text'])[:20]
        _start = _plain(ctx).find(_needle)
        if _start >= 0 and _pos_line >= 0:
            pos = _start + _pos_line
        else:
            pos = _plain(ctx).find(anchor)
        oi = _orig_index(ctx, max(0, pos))
        lo = max(0, oi - pad)
        hi = min(len(ctx), oi + len(anchor) + pad)
        out.append({'linehead': r['id'], 'book': r['book'], 'juan': r['juan'],
                    'kwic': ctx[lo:hi], 'book_counts': counts})
        if len(out) >= int(limit or 6):
            break
    return out



