# -*- coding: utf-8 -*-
"""業疏／戒疏／尼鈔校閱執行器（獨立優化版）：Qwen 為決策模型，工具為 DeepSeek Search／Fetch。

主要優化：
1. 按需檢索＋單組最多 8 輪工具
2. Search 開啟 need_content=True＋白名單關鍵字視窗擷取
3. 內建 SQLite 本地快取（同查詢只付一次錢）
4. Fetch 支援 keyword 精準定位抽取前後文
5. 啟動前實測 DeepSeek API；401/402 立即觸發 STOP 止血；429/5xx 指數退避重試＋併發限流

用法：
  $env:QWEN_SHUJI_SRC='鋪開_全部'
  python -X utf8 _src/qwen_local.py
"""
import hashlib
import io
import json
import os
import random
import re
import signal
import sqlite3
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, '測試', os.environ.get('QWEN_SHUJI_SRC', '業疏_疏記20組'))
OUT = os.path.join(SRC, '回覆')
STOP = os.path.join(SRC, 'STOP')
STOP_GLOBAL = os.path.join(B, 'STOP')

KEY = open(os.path.join(B, '.qwen_key'), encoding='utf-8-sig').read().strip()
_ds_path = os.path.join(B, '.deepseek_key')
DS_KEY = open(_ds_path, encoding='utf-8-sig').read().strip() if os.path.exists(_ds_path) else ''

QWEN_BASE = 'https://token-plan.maas.qwencloudapi.com/compatible-mode/v1'
MODEL = os.environ.get('QWEN_MODEL', 'qwen4-max-preview')
REASONING_EFFORT = os.environ.get('QWEN_EFFORT', 'xhigh')
MAX_TOOL_ROUNDS = 8
WORKERS = int(os.environ.get('QWEN_WORKERS', '0'))  # 0＝依待送份數自動（上限 40）

DS_SEARCH = 'https://api.deepseek.com/v1/tools/search'
DS_FETCH = 'https://api.deepseek.com/v1/tools/fetch'

# 放本機 AppData 避免 OneDrive 頻繁鎖檔；若無則退回 B
_cache_dir = os.environ.get('LOCALAPPDATA') or B
CACHE_DB = os.path.join(_cache_dir, 'xw_deepseek_cache.sqlite')

os.makedirs(OUT, exist_ok=True)

WHITELIST = (
    'tripitaka.cbeta.org', 'cbetaonline.dila.edu.tw', 'cbeta.buddhism.org.hk',
    'zh.wikisource.org', 'zh.m.wikisource.org',
    'ctext.org', 'glossaries.dila.edu.tw', 'diancang.xyz',
    'zhonghuadiancang.com', 'buddhism.org.hk',
)

_ds_search_sem = threading.Semaphore(10)
_stale_lock = threading.Lock()
_ds_fetch_sem = threading.Semaphore(6)  # 防止同時猛打單一佛典網站觸發 429/503
_cache_lock = threading.Lock()
_inflight = {}          # key -> Event，避免同關鍵詞同時重複付費
_inflight_lock = threading.Lock()

MAX_SEARCH_PER_GROUP = int(os.environ.get('QWEN_MAX_SEARCH', '3'))
MAX_FETCH_PER_GROUP = int(os.environ.get('QWEN_MAX_FETCH', '1'))


_FATAL = []


class FatalAPIError(RuntimeError):
    """401 / 402 等憑證或餘額不足錯誤，應立即中止批次以免空轉浪費額度。"""


HAN_CHK = re.compile(r'[\u4e00-\u9fff]')


SRC_RE_ALL = re.compile(r'■ (?:疏文|記文|鈔文|律文|註文|序文)（原文）(?:\[\d+\])?'
                        r'\s*\n+(.+?)(?=\n+■ |\n+【(?:後文背景|待審譯文|裁決分歧參考|分段要求|目前譯文|舊譯參考)|\Z)', re.S)


def _raw_len(text):
    parts = SRC_RE_ALL.findall(text)
    body = ''.join(parts) if parts else text
    return len(HAN_CHK.findall(body))


def _han_len(text):
    return len(HAN_CHK.findall(text))


def _local_cap(text):
    """依待審原文長度決定本地檢索上限。"""
    n = _raw_len(text)
    if n <= 30:
        return 1
    if n < 100:
        return 2
    if n <= 300:
        return 3
    return 5


def _quota(text):
    """依待審原文長度決定 (搜尋上限, 抓取上限)；環境變數可單獨覆寫。"""
    n = _raw_len(text)
    fetch = int(os.environ['QWEN_MAX_FETCH']) if os.environ.get('QWEN_MAX_FETCH') else 1
    if os.environ.get('QWEN_MAX_SEARCH'):
        return MAX_SEARCH_PER_GROUP, fetch
    if n < 100:
        return 1, fetch
    if n <= 300:
        return 2, fetch
    return 2, fetch


NO_WEB = os.environ.get('QWEN_NO_WEB') == '1'
_LOCAL = os.environ.get('QWEN_LOCAL') == '1'
KEEP_THINKING = os.environ.get('QWEN_KEEP_THINKING', '1') == '1'

LOCAL_SCHEMAS = [
    {'type': 'function', 'function': {
        'name': 'local_search',
        'description': '檢索本地書庫（33 部，書名可寫簡稱或全稱）。一次即回傳命中行與前後文（含 linehead）。',
        'parameters': {'type': 'object', 'properties': {
            'query': {'type': 'string', 'description': '3~10 字純原文核心詞（不要包含書名；書名請填 work 欄位）'},
            'work': {'type': 'string', 'description': '選填，限定書名'},
            'rows': {'type': 'integer'},
        }, 'required': ['query']},
    }},
]


if _LOCAL:
    import sys
    sys.path.insert(0, os.path.join(B, '_src'))
    import local_corpus as _LC

    MAX_LOCAL_PER_GROUP = int(os.environ.get('QWEN_MAX_LOCAL', '5'))

    def _local_budget(stats):
        if stats is None:
            return True
        if stats.get('locals', 0) >= stats.get('local_cap', MAX_LOCAL_PER_GROUP):
            stats['local_denied'] = stats.get('local_denied', 0) + 1
            return False
        stats['locals'] = stats.get('locals', 0) + 1
        return True

    def local_search(query, work=None, rows=4, stats=None, **kwargs):
        if work is None:
            work = kwargs.get('book') or kwargs.get('work_name')
        rows = kwargs.get('limit') or kwargs.get('count') or rows or 4
        rows = min(max(int(rows), 1), 5)
        log = stats.setdefault('local_log', []) if stats is not None else []
        key = (str(query).strip(), str(work or '').strip())
        memo = stats.setdefault('local_memo', {}) if stats is not None else {}
        if key in memo:
            stats['local_repeat'] = stats.get('local_repeat', 0) + 1
            log.append({'q': key[0], 'work': key[1], 'repeat': True, 'n': memo[key]})
            return json.dumps({'num_found': memo[key],
                               'results': memo.get(('R',) + key, []),
                               'note': '同一查詢已執行過，直接沿用結果（不計額度）'},
                              ensure_ascii=False)
        _toks = [x for x in re.split(r'[\s　]+', str(query)) if x]
        if not _toks:
            return json.dumps({'error': '查詢為空，請提供 2 字以上實詞'}, ensure_ascii=False)
        if any(len(x) < 2 for x in _toks) and (stats or {}).get('badq', 0) < 1:
            if stats is not None:
                stats['badq'] = stats.get('badq', 0) + 1
            return json.dumps({'error': '查詢含單字實詞，請改用 2 字以上實詞或加長詞組'},
                              ensure_ascii=False)
        if not _local_budget(stats):
            log.append({'q': key[0], 'work': key[1], 'denied': True})
            return json.dumps({'error': '本地檢索已達上限（%d 次），請直接完成判定。'
                                        % stats.get('local_cap', MAX_LOCAL_PER_GROUP)},
                              ensure_ascii=False)
        hits = _LC.find(query, work, rows)
        if stats is not None:
            log.append({'q': key[0], 'work': key[1], 'n': len(hits)})
        relaxed = False
        _own = (stats or {}).get('own_text') or ''
        _raw_n = len(hits)
        _own = re.sub(r'[0-9]+', '', _own)
        _wins = ([_own[i:i + 20] for i in range(0, max(1, len(_own) - 19), 10)
                  if len(_own) >= 12] if _own else [])
        _cur_book = (stats or {}).get('book') or ''
        if _own and hits:
            _keep = []
            for h in hits:
                _ht = re.sub(r'[\W_]+', '', (h.get('kwic') or '') + (h.get('line') or '')).translate(_VAR_MAP)
                if h.get('book') in ('濟緣記', '行宗記', '資持記', '業疏科', '戒疏科', '行事鈔科', '義鈔科', '尼鈔科', '南山律學辭典'):
                    _keep.append(h)
                    continue
                if _cur_book and h.get('book') == _cur_book and any(
                        w and w in _ht for w in _wins):
                    continue
                if not _cur_book and any(w and w in _ht for w in _wins):
                    continue
                _keep.append(h)
            hits = _keep
        if not hits and work:
            hits = _LC.find(query, None, rows)
            relaxed = True
            _raw2 = len(hits)
            if _own and hits:
                _keep = []
                for h in hits:
                    _ht = re.sub(r'[\W_]+', '', (h.get('kwic') or '') + (h.get('line') or '')).translate(_VAR_MAP)
                    if h.get('book') in ('濟緣記', '行宗記', '資持記', '業疏科', '戒疏科', '行事鈔科', '義鈔科', '尼鈔科', '南山律學辭典'):
                        _keep.append(h)
                        continue
                    if any(w and w in _ht for w in _wins):
                        continue
                    _keep.append(h)
                hits = _keep
        if stats is not None:
            memo[key] = len(hits)
            memo[('R',) + key] = hits
        if not hits and stats is not None and stats.get('refund', 0) < 2:
            stats['refund'] = stats.get('refund', 0) + 1
            stats['locals'] = max(0, int(stats.get('locals', 1)) - 1)
        payload = {'num_found': len(hits), 'results': hits}
        if relaxed and hits:
            payload['note'] = ('原指定《%s》查無，已改從全庫查得；'
                               '請依各筆 book 欄位確認實際所屬部別。' % work)
        counts = hits[0].get('book_counts') if hits else None
        for h in hits:
            h.pop('book_counts', None)
        if counts:
            payload['book_counts'] = counts
        if stats is not None:
            _cap = stats.get('local_cap', MAX_LOCAL_PER_GROUP)
            payload['remaining'] = max(0, _cap - stats.get('locals', 0))
        if stats is not None and stats.get('locals', 0) >= stats.get('local_cap', MAX_LOCAL_PER_GROUP):
            payload['notice'] = ('這是最後一次本地檢索額度，請勿再呼叫 local_search，'
                                 '直接依據現有資料完成判定。')
        return json.dumps(payload, ensure_ascii=False)


def _init_cache():
    with _cache_lock:
        con = sqlite3.connect(CACHE_DB, timeout=30)
        con.execute(
            'CREATE TABLE IF NOT EXISTS ds_cache ('
            'k TEXT PRIMARY KEY, kind TEXT, payload TEXT, created_at REAL)'
        )
        con.commit()
        con.close()


def _cache_get(key):
    try:
        with _cache_lock:
            con = sqlite3.connect(CACHE_DB, timeout=15)
            row = con.execute('SELECT payload FROM ds_cache WHERE k = ? AND created_at > ?',
                          (key, time.time() - 30 * 86400)).fetchone()
            con.close()
        return json.loads(row[0]) if row else None
    except Exception:
        return None


def _cache_set(key, kind, data):
    try:
        raw = json.dumps(data, ensure_ascii=False)
        with _cache_lock:
            con = sqlite3.connect(CACHE_DB, timeout=15)
            con.execute(
                'INSERT OR REPLACE INTO ds_cache (k, kind, payload, created_at) VALUES (?, ?, ?, ?)',
                (key, kind, raw, time.time()),
            )
            con.commit()
            con.close()
    except Exception:
        pass


def _allowed(u):
    try:
        host = urllib.parse.urlparse(u).netloc.lower().split(':')[0]
    except Exception:
        return False
    return any(host == w or host.endswith('.' + w) for w in WHITELIST)


_VAR_MAP = str.maketrans('煑竪虗汙竝説爲於着衆盋鉢艸羣裏呪眞婬覩牀徧却麤纔',
                         '煮豎虛污並說為于著眾缽缽草群裡咒真淫睹床遍卻粗才')
_STRIP_RE = re.compile(r'[^\u4e00-\u9fffA-Za-z0-9]')


def _norm_with_map(s):
    chars, idx_map = [], []
    for idx, ch in enumerate(s):
        if _STRIP_RE.match(ch):
            continue
        chars.append(ch.translate(_VAR_MAP))
        idx_map.append(idx)
    return ''.join(chars), idx_map


def _extract_window(text, query, radius=1800, max_len=3600):
    """去標點＋異體字正規化後定位最密視窗，同分取較後位置避開網頁頂端標題列。"""
    if not text:
        return ''
    if len(text) <= max_len:
        return text

    clean_q = re.sub(r'site:\S+|["「」『』《》〈〉、，。；：？！\s]+', ' ', query or '').strip()
    raw_tokens = [t for t in clean_q.split() if len(t) >= 2]
    norm_tokens = [_STRIP_RE.sub('', t).translate(_VAR_MAP) for t in raw_tokens]
    norm_tokens = [t for t in norm_tokens if len(t) >= 2]
    if not norm_tokens:
        return text[:max_len] + '\n…（無查詢詞，僅示開頭）'

    plain_text, idx_map = _norm_with_map(text)
    positions = []
    for t in norm_tokens:
        start, hit = 0, 0
        while hit < 20:
            i = plain_text.find(t, start)
            if i < 0:
                break
            positions.append((idx_map[i], t))
            start = i + len(t)
            hit += 1

    if not positions:
        probes = []
        for t in norm_tokens:
            if len(t) >= 4:
                probes.extend(t[k:k + 3] for k in range(0, len(t) - 2))
        for p in probes[:12]:
            start, hit = 0, 0
            while hit < 10:
                i = plain_text.find(p, start)
                if i < 0:
                    break
                positions.append((idx_map[i], p))
                start = i + len(p)
                hit += 1
        if not positions:
            return text[:max_len] + '\n…（未定位到關鍵字，僅示開頭）'
        norm_tokens = list(dict.fromkeys(probes))

    best_lo, best_hi, best_score, best_center = 0, min(len(text), max_len), -1, -1
    for i, _t in positions:
        lo = max(0, i - radius)
        hi = min(len(text), i + radius)
        win_norm = _STRIP_RE.sub('', text[lo:hi]).translate(_VAR_MAP)
        score = sum(1 for t in norm_tokens if t in win_norm)
        center = (lo + hi) // 2
        if score > best_score or (score == best_score and center > best_center):
            best_lo, best_hi, best_score, best_center = lo, hi, score, center

    if best_hi - best_lo > max_len:
        center = min(positions, key=lambda p: abs(p[0] - (best_lo + best_hi) // 2))[0]
        best_lo = max(0, center - max_len // 2)
        best_hi = min(len(text), best_lo + max_len)

    prefix = '…（前略）\n' if best_lo > 0 else ''
    suffix = '\n…（後略）' if best_hi < len(text) else ''
    return prefix + text[best_lo:best_hi] + suffix



def _ds_post(url, payload, sem, timeout=90):
    if not DS_KEY:
        raise FatalAPIError('未設定 .deepseek_key')
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    for attempt in range(4):
        _wait = 0.0
        try:
            with sem:
                req = urllib.request.Request(
                    url, data=data,
                    headers={'Authorization': 'Bearer ' + DS_KEY,
                             'Content-Type': 'application/json'}, method='POST')
                raw = urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8')
            return json.loads(raw)
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')[:240]
            if e.code in (401, 402):
                raise FatalAPIError('DeepSeek HTTP %d（金鑰無效或餘額不足）: %s' % (e.code, body))
            if e.code in (408, 429, 500, 502, 503, 504) and attempt < 3:
                _wait = (1.5 * (2 ** attempt)) + random.uniform(0.1, 0.8)
            else:
                raise RuntimeError('DeepSeek HTTP %d: %s' % (e.code, body))
        except Exception as e:
            if attempt < 3:
                _wait = 1.5 * (2 ** attempt)
            else:
                raise
        if _wait:
            if _stop_requested():
                raise FatalAPIError('STOP')
            time.sleep(_wait)

def _cached_or_fetch(ck, kind, do_call):
    hit = _cache_get(ck)
    if hit is not None:
        return hit, True
    with _inflight_lock:
        ev = _inflight.get(ck)
        owner = ev is None
        if owner:
            ev = threading.Event()
            _inflight[ck] = ev
    if not owner:
        ev.wait(timeout=180)
        hit = _cache_get(ck)
        return (hit, True) if hit is not None else (None, False)
    try:
        data = do_call()
        _empty = (isinstance(data, dict) and not (data.get('results') or data.get('hits')))
        if isinstance(data, dict) and not _empty:
            _cache_set(ck, kind, data)
        return data, False
    finally:
        with _inflight_lock:
            _inflight.pop(ck, None)
        ev.set()


def web_search(query, ori_question=None, rows=10, stats=None, **kwargs):
    _ms = (stats or {}).get('max_search', MAX_SEARCH_PER_GROUP)
    if stats is not None:
        if stats.get('searches', 0) >= _ms:
            return json.dumps({'error': '本組搜尋已達上限（%d 次），請直接用現有資料完成判定。'
                                        % _ms}, ensure_ascii=False)
        stats['searches'] = stats.get('searches', 0) + 1
        stats.setdefault('queries', []).append(str(query)[:60])

    q = str(query).strip()[:128]
    cnt = min(max(int(rows or 15), 10), 25)
    ck = hashlib.sha256(('search|%d|%s' % (cnt, q)).encode('utf-8')).hexdigest()

    def _call():
        payload = {'query': q, 'count': cnt, 'need_content': True}
        if ori_question:
            payload['ori_question'] = str(ori_question).strip()[:128]
        if stats is not None:
            stats['ds_calls'] += 1
        return _ds_post(DS_SEARCH, payload, _ds_search_sem, timeout=90)

    r, from_cache = _cached_or_fetch(ck, 'search', _call)
    if r is None:
        return json.dumps({'error': '搜尋暫時失敗'}, ensure_ascii=False)
    if from_cache and stats is not None:
        stats['cache_hits'] += 1

    ranked = sorted(r.get('results') or [],
                    key=lambda x: (_allowed(x.get('url') or ''),
                                   float(x.get('rerank_score') or 0.0)), reverse=True)
    out = []
    budget = 2
    for x in ranked:
        u = x.get('url') or ''
        if not _allowed(u):
            continue
        item = {'title': (x.get('title') or '')[:100], 'url': u, 'trusted': True,
                'summary': (x.get('summary') or '')[:300]}
        raw = x.get('content') or ''
        if raw and budget > 0:
            item['excerpt'] = _extract_window(raw, q, radius=450, max_len=900)
            budget -= 1
        stats.setdefault('hits', []).append(
            {'q': q[:40], 'url': u[:120], 'title': item['title'][:60]})
        out.append(item)
        if len(out) >= 3:
            break

    if not out:
        return json.dumps({'results': [], 'note': '查無白名單來源（非白名單結果已略去）'},
                          ensure_ascii=False)
    return json.dumps({'results': out}, ensure_ascii=False)


def web_fetch(url, keyword=None, stats=None, **kwargs):
    _mf = (stats or {}).get('max_fetch', MAX_FETCH_PER_GROUP)
    if stats is not None:
        if stats.get('fetches', 0) >= _mf:
            return json.dumps({'error': '本組抓取已達上限（%d 次），請直接判定。'
                                        % _mf}, ensure_ascii=False)
        stats['fetches'] = stats.get('fetches', 0) + 1

    u = str(url).strip()
    if not _allowed(u):
        return json.dumps({'error': '網域不在白名單，請改用其他來源', 'url': u}, ensure_ascii=False)

    ck = hashlib.sha256(('fetch|' + u).encode('utf-8')).hexdigest()

    def _call():
        if stats is not None:
            stats['ds_calls'] += 1
        return _ds_post(DS_FETCH, {'url': u}, _ds_fetch_sem, timeout=120)

    r, from_cache = _cached_or_fetch(ck, 'fetch', _call)
    if r is None:
        return json.dumps({'error': '抓取暫時失敗'}, ensure_ascii=False)
    if from_cache and stats is not None:
        stats['cache_hits'] += 1

    c = r.get('content') or ''
    excerpt = _extract_window(c, keyword or '', radius=1800, max_len=3600)
    return json.dumps({'url': u, 'total_chars': len(c), 'content': excerpt},
                      ensure_ascii=False)


TOOLS = [
    {
        'type': 'function',
        'function': {
            'name': 'web_search',
            'description': (
                '用 DeepSeek 搜尋佛典原文與摘要（已含白名單正文片段）。'
                '查詢務必帶書名或核心名相（≤24 字，可含 site:cbetaonline.dila.edu.tw 或 site:tripitaka.cbeta.org）；'
                '非白名單來源程式已濾除，回傳僅含白名單；'
                ),
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': '4~16 字核心名相（建議「書名＋名相」，如「隨機羯磨 前六有非」「四分律 僧殘」）',
                    },
                    'ori_question': {
                        'type': 'string',
                        'description': '選填，簡短說明想確認的問題，有助搜尋重排',
                    },
                    'rows': {
                        'type': 'integer',
                        'description': '預設 10（不加價，有助篩出白名單）',
                    },
                },
                'required': ['query'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'web_fetch',
            'description': '當 web_search 的 excerpt 仍不足時，抓取指定白名單網址並定位關鍵字前後文。',
            'parameters': {
                'type': 'object',
                'properties': {
                    'url': {'type': 'string', 'description': 'web_search 回傳的網址'},
                    'keyword': {'type': 'string', 'description': '要在網頁內定位的 3~8 字核心原文詞'},
                },
                'required': ['url'],
            },
        },
    },
]

if _LOCAL:
    TOOLS += LOCAL_SCHEMAS

if _LOCAL:
    _keep = {'local_search'}
    TOOLS = [t for t in TOOLS
             if t['function']['name'] in _keep or not t['function']['name'].startswith('local_')]

if NO_WEB:
    TOOLS = [t for t in TOOLS if not t['function']['name'].startswith('web_')]

if os.environ.get('QWEN_NO_TOOLS') == '1':
    TOOLS = []  # 純文字模式（標點、修訂等）

CITE_RULE = ('查證僅供翻譯參考，嚴禁在譯文內外附帶網址、出處或說明。'
             if os.environ.get('QWEN_NO_CITE') == '1' else
             '若有查證，於理由或依據中簡註書名卷次，並摘錄關鍵原句 1–2 句，嚴禁寫入最終譯文。')

SYSTEM_PROMPT = ("""你是精通南山律宗與漢文大藏經的譯校助手，依當前任務（翻譯／裁決／審核／修訂）行事。
檢索原則：
1. 按需檢索：一般文句依本段與前後背景即可判定者，無須呼叫搜尋；僅於下列情況檢索：
   (a) 省文致義理不明，或主客、空間、開遮邏輯疑似自相矛盾；
   (b) 專名、度量數理、儀式階段或律學特定用語不確定；
   (c) 懷疑引文原意衝突或疑有訛字；
   (d) 科判層級或科名不確定。
2. 工具用法：__TOOLS__
   - local_search：支援多詞鄰近共現；短語查無時，改以空格分隔 2～3 個實詞。僅在確知要查某一部書時才填 work；查平行文或跨書用語時務必留空。跨書所得異釋僅供參照，不得硬套覆蓋本段原制與文脈。
   - 檢索節奏：顯明文意勿為求安心重複搜尋；次數以每次回傳的 `remaining` 為準，用完即不得再呼叫。
3. 典籍簡稱勿展開錯：伽論＝《薩婆多部毘尼摩得勒伽》（非《瑜伽師地論》）；婆沙／婆論／多論＝《薩婆多毘尼毘婆沙》（非《大毘婆沙論》）；善生＝《優婆塞戒經》；成論＝《成實論》；雜心＝《雜阿毘曇心論》；明了論＝《律二十二明了論》。
4. 反切音訓若無確據，保留「某某反」原訓釋字面即可，勿盲猜現代讀音。
5. 嚴禁未經檢索就憑記憶臆測經文出處或行號。__CITE__""")

if _LOCAL:
    if NO_WEB:
        _tools = ('**僅限使用 local_search 檢索本地典籍**（涵蓋南山三大部、科記、'
                  '律藏與辭典）；不確定出處時 work 請留空，以空格分隔 2～3 個實詞搜尋。')
    else:
        _tools = ('優先用 local_search（涵蓋南山三大部、科記、律藏與辭典）；'
                  '不確定出處時 work 請留空，以空格分隔 2～3 個實詞。'
                  '查無再用 web_search（同一疑點以 2～3 組核心詞為限；已能判定勿重複呼叫；'
                  '摘要已足者勿再 web_fetch），查平行文用古籍原名。')
else:
    _tools = '使用 web_search（同一疑點以 2～3 組核心詞為限），查平行文用古籍原名，勿用現代簡稱'

SYSTEM_PROMPT = (SYSTEM_PROMPT
                  .replace('__TOOLS__', _tools)
                  .replace('__CITE__', CITE_RULE))



NO_TOOLS_SYSTEM = ('你是南山律典白話譯文編輯，請僅依據提供的原文、前後背景與修訂清單'
                   '直接輸出完整白話譯文，勿輸出任何檢索或工具呼叫語法。'
                   '典籍簡稱：伽論＝《薩婆多部毘尼摩得勒伽》（非瑜伽師地論）；'
                   '婆沙／多論＝《薩婆多毘尼毘婆沙》（非大毘婆沙論）；善生＝《優婆塞戒經》；'
                   '成論＝《成實論》；雜心＝《雜阿毘曇心論》；明了論＝《律二十二明了論》。'
                   '體例：原文夾注與讀音得保留，其餘不加解說括號；脫訛用〔補字〕／〔疑作X〕；'
                   '古制度量保留原稱；反切音訓保留「某某反」原訓釋字面即可，勿盲猜現代讀音；'
                   '無實質文義之空符號不強留。'
                   '若任務禁止標註出處（NO_CITE），不得在譯文中寫書名卷次或網址。')

if os.environ.get('QWEN_NO_TOOLS') == '1':
    SYSTEM_PROMPT = NO_TOOLS_SYSTEM


def qwen_post(payload):
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    for attempt in range(6):
        req = urllib.request.Request(
            QWEN_BASE + '/chat/completions',
            data=data,
            headers={
                'Authorization': 'Bearer ' + KEY,
                'Content-Type': 'application/json',
            },
            method='POST',
        )
        try:
            raw = urllib.request.urlopen(req, timeout=600).read().decode('utf-8')
            return json.loads(raw)
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')[:240]
            if e.code in (401, 402):
                raise FatalAPIError(f'Qwen HTTP {e.code}（金鑰無效或額度異常）: {body}')
            if e.code == 429 and 'insufficient_quota' in body:
                raise FatalAPIError('Qwen 額度已用盡（insufficient_quota）: ' + body)
            if e.code in (408, 429, 500, 502, 503, 504) and attempt < 5:
                wait_sec = min(90, (5 * (2 ** attempt)) + random.uniform(0.5, 3.0))
                if _stop_requested():
                    raise FatalAPIError('STOP')
                time.sleep(wait_sec)
                continue
            raise RuntimeError(f'Qwen HTTP {e.code}: {body}')
        except Exception as e:
            if attempt < 5:
                time.sleep(min(45, 4 * (attempt + 1) + random.uniform(0.5, 2.0)))
                continue
            raise RuntimeError(str(e))



HAN = re.compile(r'[\u4e00-\u9fff]')


def _split_col3(out):
    """切出第 3 欄（修正後／修訂後／定稿／最終譯文）：回傳 (前段, 第3欄)。"""
    m = re.search(r'(?:^|\n)[^\n]{0,40}?(?:修正後|修訂後|定稿|最終)(?:的)?譯文[\*\s：:]*', out)
    if not m:
        return '', out
    i = m.start()
    j = m.end()
    body = _strip_fence(out[j:].lstrip('*：: \t\r\n'))
    if body[:1] in ('（', '('):
        _m = re.match(r'[（(][^）)]*[）)]\s*[：:]?\s*\n?', body)
        if _m and re.search(r'註|注|按|說明|沿用|未改|以下|全文|白話|修訂|完整', _m.group(0)):
            body = body[_m.end():]
    return out[:j].rstrip() + '\n\n', body

def _src_unit(src_text):
    """從材料取出待審原文（■ 疏文（原文）之後那段）。"""
    m = re.search(r'■ (?:疏文|記文|鈔文|律文|註文|序文)（原文）(?:\[\d+\])?\s*\n+(.+?)(?=\n\n■ |\n+【(?:後文背景|待審譯文|裁決分歧參考|目前譯文|分段要求|舊譯參考)|\Z)', src_text, re.S)
    return m.group(1).strip() if m else ''


def _strip_fence(out):
    return re.sub(r'(?m)^\s*```[a-zA-Z]*\s*$', '', out or '').strip()


def _strip_dup_labels(out):
    """同一欄位標籤只保留第一次出現，後續段落的重複標籤剝掉。

    只應作用於第 3 欄；若對整份回覆掃描，會誤把第 3 欄開頭的真標籤當重複剝掉。
    """
    seen = set()
    res = []
    for ln in out.split('\n'):
        m = re.match(r'^(【(?:疏文|記文|鈔文|律文|註文|序文)】)\s*', ln)
        if m:
            lab = m.group(1)
            if lab in seen:
                ln = ln[m.end():]
            else:
                seen.add(lab)
        res.append(ln)
    return '\n'.join(res)


def _looks_pasted(col3, src_unit):
    """第 3 欄開頭若與待審原文前 20 漢字高度重疊，判定為重貼原文。"""
    if not src_unit:
        return False
    col3 = re.sub(r'^\s*【(?:疏文|記文|鈔文|律文|註文|序文)】\s*', '', col3 or '')
    a = ''.join(HAN.findall(col3))[:20]
    b = ''.join(HAN.findall(src_unit))[:20]
    if len(a) < 8 or len(b) < 8 or len(src_unit) <= 40:
        return False
    if len(HAN.findall(col3)) > len(HAN.findall(src_unit)) * 1.15:
        return False
    same = 0
    for x, y in zip(a, b):
        if x != y:
            break
        same += 1
    return same >= 18 and len(HAN.findall(col3)) < len(HAN.findall(src_unit)) * 1.5


def _save_result(dst, choice, stats, extra_tag='', src_text=''):
    if src_text:
        stats['src_hash'] = hashlib.md5(
            src_text.encode('utf-8')).hexdigest()[:12]
    out = _strip_fence(choice['message'].get('content') or '')
    if (len(HAN_CHK.findall(out)) < 2
            and 'PASS_A_KEEP_A' not in out and 'PASS_A' not in out):
        return ('empty', '空回覆')
    for _old_sfx in ('_截斷.txt', '_重貼原文.txt', '_400審查.txt'):
        _oldp = dst.replace('_回.txt', _old_sfx)
        if out.strip() and os.path.exists(_oldp):
            try:
                os.remove(_oldp)
            except Exception:
                pass
    for _sfx in ('_截斷.txt', '_重貼原文.txt', '_400審查.txt'):
        _old = dst.replace('_回.txt', _sfx)
        if out.strip() and os.path.exists(_old):
            try:
                os.remove(_old)
            except Exception:
                pass
    if choice.get('finish_reason') == 'content_filter':
        return ('blocked', '內容過濾')
    if os.environ.get('QWEN_RAW_SAVE') == '1':
        pass  # 保留完整報告，勿剝行首標籤
        if _looks_pasted(out, _src_unit(src_text)):
            stats['pasted_source'] = True
            extra_tag += ', 疑似重貼原文'
            _bad = dst.replace('_回.txt', '_重貼原文.txt')
            io.open(_bad, 'w', encoding='utf-8').write(out)
            return ('pasted', '貼原文')
        if os.environ.get('QWEN_NO_CITE') == '1' and re.search(
                r'https?://', out):
            stats['leak_detected'] = True
            extra_tag += ', 攔截外洩出處'
            out = re.sub(r'https?://\S+', '', out).strip()
    else:
        head, col3 = _split_col3(out)
        col3 = _strip_dup_labels(col3)
        if _looks_pasted(col3, _src_unit(src_text)):
            stats['pasted_source'] = True
            extra_tag += ', 疑似重貼原文'
        if (len(HAN_CHK.findall(col3)) < 2
                and 'PASS_A_KEEP_A' not in col3 and '沿用' not in col3):
            return ('empty', '第3欄無實質譯文')
        out = head + col3
    is_trunc = (choice.get('finish_reason') == 'length')
    target = dst.replace('_回.txt', '_截斷.txt') if is_trunc else dst
    io.open(target, 'w', encoding='utf-8').write(out)
    _st = {k: v for k, v in stats.items() if k not in ('local_memo',)}
    io.open(dst.replace('_回.txt', '_usage.json'), 'w', encoding='utf-8').write(
        json.dumps(_st, ensure_ascii=False, indent=1))
    tag = ('ds=%d, cache=%d, in=%d, out=%d%s'
           % (stats['ds_calls'], stats['cache_hits'],
              stats.get('in_tok', 0), stats.get('out_tok', 0), extra_tag))
    return ('truncated' if is_trunc else 'ok'), tag


def _fallback_no_tools(dst, text, stats):
    """400 保底：不帶任何工具，純文本單輪重跑。"""
    clean_sys = ('請只依據提供之材料完成任務，並嚴格依使用者指令格式輸出。'
                 '典籍簡稱：伽論＝薩婆多部毘尼摩得勒伽；婆沙／多論＝薩婆多毘尼毘婆沙；'
                 '善生＝優婆塞戒經；成論＝成實論；雜心＝雜阿毘曇心論。')
    r2 = qwen_post({'model': MODEL,
                    'messages': [{'role': 'system', 'content': clean_sys},
                                 {'role': 'user', 'content': text}],
                    'enable_thinking': True,
                    'reasoning_effort': REASONING_EFFORT})
    u2 = r2.get('usage') or {}
    stats['out_tok'] = stats.get('out_tok', 0) + int(u2.get('completion_tokens') or 0)
    stats['in_tok'] = stats.get('in_tok', 0) + int(u2.get('prompt_tokens') or 0)
    stats['fallback_no_tools'] = True
    return _save_result(dst, r2['choices'][0], stats, ', no_tools_fallback', src_text=text)


def _save_blocked(dst, err, stats):
    """內容審查未通過：不重跑，只把錯誤與用量存檔，留待人工或換模型處理。"""
    p = dst.replace('_回.txt', '_400審查.txt')
    io.open(p, 'w', encoding='utf-8').write(
        '內容審查未通過（未重跑，待處理）\n\n'
        '錯誤：%s\n\n'
        '用量：%s\n\n搜尋軌跡：\n%s\n' % (
            err,
            json.dumps(stats, ensure_ascii=False, indent=1),
            '\n'.join('  - ' + q for q in stats.get('queries', [])) or '（無）'))
    return p


def run(f):
    src = os.path.join(SRC, f)
    dst = os.path.join(OUT, f.replace('.md', '_回.txt'))
    _u = dst.replace('_回.txt', '_usage.json')
    if os.environ.get('QWEN_SKIP_400', '1') != '0' and os.path.exists(
            dst.replace('_回.txt', '_400審查.txt')):
        return (f, 'skip-400')
    text = io.open(src, encoding='utf-8').read()
    _bm = re.search(r'（出處：《([^》]+)》', text)
    stats_book = _bm.group(1) if _bm else ''
    if os.path.exists(dst) and os.path.getsize(dst) > 10 and os.path.exists(_u):
        try:
            _uh = json.load(io.open(_u, encoding='utf-8')).get('src_hash')
            _sh = hashlib.md5(text.encode('utf-8')).hexdigest()[:12]
            if _uh and _uh != _sh:
                _uh = None
        except Exception:
            _uh = None
        # 防呆：材料比回覆新 → 視為過期，重跑（避免材料重產後錯位）
        if _uh is None or os.path.getmtime(src) > os.path.getmtime(dst) + 1:
            with _stale_lock:
                io.open(os.path.join(OUT, '_STALE.txt'), 'a', encoding='utf-8').write(f + '\n')
        else:
            return (f, 'skip')

    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': text},
    ]
    _ms, _mf = _quota(text)
    stats_cap = _local_cap(text)
    stats = {'ds_calls': 0, 'cache_hits': 0, 'max_search': _ms, 'max_fetch': _mf}
    _unit = text
    for _h in ('【本次待審單元】', '【本次待譯單元】', '【原文】'):
        if _h in text:
            _unit = text.split(_h)[-1]
            break
    else:
        _unit = ''
    _head = _unit.split('【後文背景')[0].split('【待審譯文')[0].split('【分段要求')[0]
    _pn = (len(re.findall(r'(?m)^\s*\[\d+\]', _head))
           + len(re.findall(r'（原文）\[\d+\]', _head)))
    _bonus = int(os.environ.get('QWEN_LOCAL_BONUS', '0') or '0')
    stats_cap = min(6 + _bonus, stats_cap + _bonus + max(0, _pn - 1))
    _env_cap = os.environ.get('QWEN_MAX_LOCAL')
    if _env_cap and _env_cap.isdigit():
        stats_cap = int(_env_cap)
    stats['local_cap'] = stats_cap
    stats['book'] = stats_book
    stats['own_text'] = re.sub(r'[\W_]+', '', ''.join(SRC_RE_ALL.findall(text)).translate(_VAR_MAP))

    try:
        for _round in range(MAX_TOOL_ROUNDS):
            _exhausted = (stats.get('locals', 0) >= stats.get('local_cap', 5)
                          and stats.get('ds_calls', 0) >= _ms
                          and stats.get('fetches', 0) >= _mf)
            payload = {
                'model': MODEL,
                'messages': messages,
                'enable_thinking': True,
                'reasoning_effort': REASONING_EFFORT,
                'preserve_thinking': KEEP_THINKING,
            }
            if TOOLS:
                payload['tools'] = TOOLS
                payload['tool_choice'] = 'none' if _exhausted else 'auto'
            r = qwen_post(payload)
            u = r.get('usage') or {}
            stats['out_tok'] = stats.get('out_tok', 0) + int(u.get('completion_tokens') or 0)
            stats['in_tok'] = stats.get('in_tok', 0) + int(u.get('prompt_tokens') or 0)
            choice = r['choices'][0]
            msg = choice['message']

            assistant_msg = {
                'role': 'assistant',
                'content': msg.get('content') or '',
            }
            if KEEP_THINKING and msg.get('reasoning_content'):
                assistant_msg['reasoning_content'] = msg['reasoning_content']
            if msg.get('tool_calls'):
                assistant_msg['tool_calls'] = msg['tool_calls']
            messages.append(assistant_msg)

            tool_calls = msg.get('tool_calls') or []
            print('  [%s] round %d/%d  tools=%s  in=%d out=%d  ds=%d cache=%d'
                  % (f.replace('.md', ''), _round + 1, MAX_TOOL_ROUNDS,
                     ','.join(tc['function']['name'] for tc in tool_calls) or '(final)',
                     stats.get('in_tok', 0), stats.get('out_tok', 0),
                     stats['ds_calls'], stats['cache_hits']), flush=True)

            if not tool_calls:
                st, tag = _save_result(dst, choice, stats, src_text=text)
                return (f, '%s (%s)' % (st, tag))

            for tc in tool_calls:
                fn_name = tc['function']['name']
                try:
                    args = json.loads(tc['function'].get('arguments') or '{}')
                    if fn_name == 'web_search':
                        result = web_search(**args, stats=stats)
                    elif fn_name == 'web_fetch':
                        result = web_fetch(**args, stats=stats)
                    elif fn_name == 'local_search' and _LOCAL:
                        result = local_search(**args, stats=stats)
                    else:
                        result = f'未知工具: {fn_name}'
                except FatalAPIError:
                    raise
                except Exception as e:
                    result = json.dumps({'error': f'工具執行錯誤: {e}'}, ensure_ascii=False)

                messages.append({
                    'role': 'tool',
                    'tool_call_id': tc['id'],
                    'content': result,
                })

        messages.append({
            'role': 'user',
            'content': '已達工具檢索輪數上限，請直接依原本任務規定之格式輸出最終結果。',
        })
        payload['tools'] = TOOLS
        payload['tool_choice'] = 'none'
        payload.update({'model': MODEL, 'messages': messages, 'enable_thinking': True,
                        'reasoning_effort': REASONING_EFFORT, 'preserve_thinking': KEEP_THINKING})
        r = qwen_post(payload)
        u = r.get('usage') or {}
        stats['out_tok'] = stats.get('out_tok', 0) + int(u.get('completion_tokens') or 0)
        stats['in_tok'] = stats.get('in_tok', 0) + int(u.get('prompt_tokens') or 0)
        st, tag = _save_result(dst, r['choices'][0], stats, ', max_rounds', src_text=text)
        return (f, '%s (%s)' % (st, tag))

    except FatalAPIError as e:
        _FATAL.append(str(e))
        try:
            io.open(STOP, 'w', encoding='utf-8').write(str(e))
            io.open(STOP_GLOBAL, 'w', encoding='utf-8').write(str(e))
        except Exception:
            pass
        return (f, f'FATAL: {e}')
    except RuntimeError as e:
        msg = str(e)
        if 'HTTP 400' in msg and 'data_inspection_failed' in msg:
            if os.environ.get('QWEN_400_FALLBACK') == '1':
                try:
                    st, tag = _fallback_no_tools(dst, text, stats)
                    return (f, '%s (%s)' % (st, tag))
                except Exception as e2:
                    _save_blocked(dst, '%s / 保底也失敗: %s' % (msg, e2), stats)
                    return (f, '400_blocked (已存檔)')
            _save_blocked(dst, msg, stats)
            return (f, '400_blocked (已存檔，未重跑)')
        return (f, msg)
    except Exception as e:
        return (f, str(e))


def test_apis():
    if not DS_KEY:
        raise RuntimeError(f'找不到 DeepSeek Key 檔案: {_ds_path}')
    print(f'測試 DeepSeek Search API 中 (cache={CACHE_DB})...', flush=True)
    r = _ds_post(DS_SEARCH, {'query': '四分律', 'count': 1, 'need_content': False},
                 _ds_search_sem, timeout=30)
    print(f'DeepSeek 連線成功！測試回傳筆數: {len(r.get("results") or [])}', flush=True)


def _stop_requested():
    """批次目錄或專案根目錄任一處有 STOP 檔即停。"""
    return os.path.exists(STOP) or os.path.exists(STOP_GLOBAL)


def main():
    _init_cache()
    # start 清舊旗標，避免 --wait 搶跑
    for _f in ('.stage_done', '.stage_partial'):
        _p = os.path.join(OUT, _f)
        if os.path.exists(_p):
            os.remove(_p)
    _files = sorted(x for x in os.listdir(SRC) if x.endswith('.md'))
    _skip400 = os.environ.get('QWEN_SKIP_400', '1') != '0'
    _todo = [x for x in _files
             if not (_skip400 and os.path.exists(os.path.join(OUT, x[:-3] + '_400審查.txt')))
             and not (os.path.exists(os.path.join(OUT, x[:-3] + '_回.txt')))]
    if (_todo and os.environ.get('QWEN_NO_WEB') != '1'
            and os.environ.get('QWEN_NO_TOOLS') != '1' and MAX_SEARCH_PER_GROUP > 0):
        test_apis()
    files = sorted(x for x in os.listdir(SRC) if x.endswith('.md'))
    global WORKERS
    if not WORKERS:
        WORKERS = max(1, min(len(files) or 1, 40))
    print(
        f'待送 {len(files)} 份｜併發 {WORKERS}｜模型 {MODEL}｜effort={REASONING_EFFORT}'
        f'｜max_rounds={MAX_TOOL_ROUNDS}｜max_completion_tokens=未設',
        flush=True,
    )

    stop = threading.Event()

    def _handler(signum, frame):
        if not stop.is_set():
            print('  ⏸ 收到停止訊號：不再送出新工作，等進行中的請求完成…', flush=True)
        stop.set()

    for _sig in ('SIGINT', 'SIGTERM', 'SIGBREAK'):
        try:
            signal.signal(getattr(signal, _sig), _handler)
        except Exception:
            pass

    ok = fail = 0
    inflight = {}
    it = iter(files)
    pending = len(files)

    def _submit_next(ex):
        nonlocal pending
        while len(inflight) < WORKERS:
            if _stop_requested():
                return
            try:
                f = next(it)
            except StopIteration:
                return
            pending -= 1
            inflight[ex.submit(run, f)] = f

    if _LOCAL:
        _LC.load()
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        _submit_next(ex)
        while inflight:
            done, _ = wait(inflight, return_when=FIRST_COMPLETED)
            for fu in done:
                f = inflight.pop(fu)
                try:
                    _, st = fu.result()
                except Exception as e:
                    st = f'err: {e}'
                if st == 'skip' or st.startswith('ok'):
                    ok += 1
                    print(' ', st, f, flush=True)
                else:
                    fail += 1
                    print('  ✗', f, st, flush=True)
            _submit_next(ex)

    remaining = pending + len(inflight)
    if _FATAL:
        try:
            io.open(os.path.join(OUT, '.stage_partial'), 'w', encoding='utf-8').write('FATAL\n')
            io.open(STOP_GLOBAL, 'w', encoding='utf-8').write(_FATAL[0])
        except Exception:
            pass
        print('FATAL：憑證或餘額異常，已中止', flush=True)
        sys.exit(2)
    if _stop_requested():
        marker = os.path.join(OUT, 'STOPPED.txt')
        try:
            io.open(marker, 'w', encoding='utf-8').write(
                '已優雅停止 %s\n完成 %d、失敗 %d、未送 %d\n'
                % (time.strftime('%Y-%m-%d %H:%M:%S'), ok, fail, remaining))
        except Exception:
            pass
        print(f'已停止：完成 {ok}、失敗 {fail}、未送 {remaining}（重跑會自動跳過已完成）', flush=True)
    else:
        try:
            _opp = os.path.join(OUT, '.stage_done' if fail else '.stage_partial')
            if os.path.exists(_opp):
                os.remove(_opp)
            if fail == 0:
                _pp = os.path.join(OUT, '.stage_partial')
                if os.path.exists(_pp):
                    os.remove(_pp)
            _flag = '.stage_done' if fail == 0 else '.stage_partial'
            io.open(os.path.join(OUT, _flag), 'w', encoding='utf-8').write(
                'done %s ok=%d fail=%d\n' % (time.strftime('%Y-%m-%d %H:%M:%S'), ok, fail))
        except Exception:
            pass
        print(f'完成 ok={ok} fail={fail}', flush=True)

if __name__ == '__main__':
    main()
