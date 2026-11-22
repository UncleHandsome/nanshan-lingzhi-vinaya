# -*- coding: utf-8 -*-
"""第一優先南山親註：從 CBETA Data API 取純文字，存 原文/<書名>.txt。

只做第一優先 11 部（見 WORKS）。輸出規格：
  - UTF-8、LF
  - 去 HTML 標籤；`<span class="lb">` 行號、`<div id="back">` 校勘腳註一律剔除
  - 雙行夾注（`small.inline-note`）保留，以〔…〕標記
  - `<p>` 段落以空行分隔；段落過長者依句末標點折行（≤ WIDTH 字）

用法：
  python -X utf8 _src/fetch_cbeta_priority1.py --dry-run
  python -X utf8 _src/fetch_cbeta_priority1.py
  python -X utf8 _src/fetch_cbeta_priority1.py --only 毗尼討要
"""
import argparse
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
YUAN = os.path.join(B, '原文')
KEY_FILE = os.path.join(B, '.cbeta_key')
CBETA_BASE = 'https://cbdata.dila.edu.tw/dev'
WIDTH = 80

# (存檔書名, CBETA work id, 備註) —— juan 清單由 /works 取得
WORKS = [
    ('四分律拾毗尼義鈔輔要記', 'X0748', '宋 允堪述'),
    ('毗尼討要', 'X0743', '唐 玄惲纂'),
    ('四分律行事鈔簡正記', 'X0737', '後唐 景霄纂'),
    ('四分律隨機羯磨疏正源記', 'X0726', '宋 允堪述'),
    ('四分律含注戒本疏發揮記', 'X0712', '宋 允堪述（殘，CBETA 僅存卷第三）'),
    ('芝苑遺編', 'X1104', '宋 元照撰（CBETA 題名作「芝園遺編」）'),
    ('量處輕重儀', 'T1895', '唐 道宣緝'),
    ('釋門歸敬儀', 'T1896', '唐 道宣述'),
    ('教誡新學比丘行護律儀', 'T1897', '唐 道宣述'),
    ('釋門章服儀', 'T1894', '唐 道宣述'),
    ('佛制比丘六物圖', 'T1900', '宋 元照撰'),
]

HAN = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]')

_last_ts = [0.0]


def _key():
    return io.open(KEY_FILE, encoding='utf-8-sig').read().strip()


def api(path, params=None):
    p = path + ('?' + urllib.parse.urlencode(params) if params else '')
    url = CBETA_BASE + p
    headers = {
        'Authorization': 'Bearer ' + _key(),
        'Referer': 'https://localhost/priority1-fetch',
        'User-Agent': 'CBETA-Priority1-Fetch/1.0',
    }
    for attempt in range(4):
        wait = 0.35 - (time.time() - _last_ts[0])
        if wait > 0:
            time.sleep(wait)
        _last_ts[0] = time.time()
        req = urllib.request.Request(url, headers=headers, method='GET')
        try:
            raw = urllib.request.urlopen(req, timeout=60).read().decode('utf-8')
            return json.loads(raw)
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')[:160]
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(3 * (attempt + 1))
                continue
            raise RuntimeError('CBETA HTTP %s：%s（%s）' % (e.code, body, p))
        except Exception as e:  # noqa: BLE001
            if attempt < 3:
                time.sleep(2 * (attempt + 1))
                continue
            raise RuntimeError('CBETA 連線失敗：%s（%s）' % (e, p))
    return {}


# ---------------------------------------------------------------- HTML 清理
_LB_RE = re.compile(r'<span class="lb"[^>]*>.*?</span>', re.S)
_LINEINFO_RE = re.compile(r"<span class='lineInfo'[^>]*>\s*</span>", re.S)
_NOTEANCHOR_RE = re.compile(r"<a class='noteAnchor'[^>]*>\s*</a>", re.S)
_FOOTNOTE_RE = re.compile(r"<span class='footnote[^>]*>.*?</span>", re.S)
_INLINE_RE = re.compile(r'<small\s+class=[\'"]inline-note[^>]*>(.*?)</small>', re.S)
_P_RE = re.compile(r'<p([^>]*)>(.*?)</p>', re.S)
_TAG_RE = re.compile(r'<[^>]+>')


_BLOCK_END_RE = re.compile(r'</(?:li|tr|h[1-6])>', re.I)
_BR_RE = re.compile(r'<br\s*/?>', re.I)
_IMG_RE = re.compile(r'<img[^>]*>', re.I)


def _strip_markup(html):
    """去行號／校勘腳註／圖檔，雙行夾注轉〔…〕，清單列轉換行；保留 <p> 供分段。

    注意：`</p>` 不可在此移除，否則 juan_blocks 的 <p> 比對會失效、卷題與夾注無法分列。
    """
    body = html.split("<div id='body'", 1)[-1]
    body = body.split('>', 1)[1] if '>' in body else body
    body = body.split("<div id='back'>", 1)[0]
    body = body.split("<div id='cbeta-copyright'>", 1)[0]
    body = _LB_RE.sub('', body)
    body = _LINEINFO_RE.sub('', body)
    body = _NOTEANCHOR_RE.sub('', body)
    body = _FOOTNOTE_RE.sub('', body)
    body = _IMG_RE.sub('', body)
    body = _INLINE_RE.sub(lambda m: '〔%s〕' % _TAG_RE.sub('', m.group(1)).strip(), body)
    body = _BLOCK_END_RE.sub('\n', body)
    return body


def _unescape(s):
    return (s.replace('&nbsp;', ' ').replace('&amp;', '&')
             .replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"'))


def _text(s):
    s = _unescape(_TAG_RE.sub('', _BR_RE.sub('\n', s)))
    return re.sub(r'[ \t\u3000]+', ' ', s).strip()


def _lines(fragment):
    """把一段 HTML／文字切成行；過長行依標點折到 WIDTH 以內。無漢字者丟棄。"""
    out = []
    for ln in _text(fragment).split('\n'):
        ln = ln.strip()
        if not ln or not HAN.search(ln):
            continue
        if len(ln) <= WIDTH:
            out.append(ln)
        else:
            out.extend(_wrap(ln))
    return out


def juan_blocks(html):
    """回傳 [(段別, 內文)]；'juan'＝卷題、'p'＝一個段落（可含多行）。

    正文外的章目／卷目次（未包 <p> 的散行、<ul><li>）照原順序保留為段落，
    不與 <p> 正文字段混併；圖檔（graphic）無文字，直接略過。
    """
    body = _strip_markup(html)
    out, pos = [], 0
    for m in _P_RE.finditer(body):
        for ln in _lines(body[pos:m.start()]):
            out.append(('p', ln))
        attr, inner = m.group(1), m.group(2)
        if "class='juan'" in attr or 'class="juan"' in attr:
            # 卷題與其夾注（科文）分列，避免卷題行混入標點而失去卷次標記
            txt = _text(inner)
            notes = re.findall(r'〔([^〕]*)〕', txt)
            title = re.sub(r'〔[^〕]*〕', '', txt).strip()
            out.append(('juan', title))
            for note in notes:
                if note.strip():
                    out.append(('p', '〔%s〕' % note.strip()))
        else:
            for ln in _lines(inner):
                out.append(('p', ln))
        pos = m.end()
    for ln in _lines(body[pos:]):
        out.append(('p', ln))
    return out


def render(book, work, meta, juans):
    paras = []
    _f = meta.get('file') or work
    _m = re.match(r'^[A-Z]+\d+n0*(\d+)$', _f)
    paras.append('No. %s %s（CBETA %s；%s；%s卷）'
                 % (_m.group(1) if _m else _f, book, _f,
                    meta.get('byline') or '', meta.get('juan') or len(juans)))
    n_han = 0
    for j in juans:
        data = api('/juans', {'work': work, 'juan': j})
        res = data.get('results') or []
        if not res:
            raise RuntimeError('%s 卷%s 取無內容' % (work, j))
        blocks = juan_blocks(res[0])
        if not blocks:
            raise RuntimeError('%s 卷%s 解析後為空' % (work, j))
        for kind, txt in blocks:
            n_han += len(HAN.findall(txt))
            paras.append(txt)
    return '\n\n'.join(paras) + '\n', n_han


_CLOSERS = '」』）〕】〉》'


def _attach_closers(segs):
    """把落在句首的收尾引號／括號還給前一句，避免行首出現 」 。"""
    out = []
    for s in segs:
        if not s.strip():
            continue
        m = re.match(r'^([%s]+)(.*)$' % _CLOSERS, s, re.S)
        if m and out:
            out[-1] = out[-1] + m.group(1)
            s = m.group(2)
            if not s.strip():
                continue
        out.append(s)
    return out


def _wrap(text, width=WIDTH):
    """段落折行：先切句末標點，過長句再依逗號類切；不加字、不刪字。"""
    sents = _attach_closers([x for x in re.split(r'(?<=[。！？])', text) if x.strip()])
    lines, cur = [], ''
    for s in sents:
        s = s.strip()
        if len(cur) + len(s) <= width:
            cur += s
            continue
        if cur:
            lines.append(cur)
        if len(s) <= width:
            cur = s
            continue
        cur = ''
        for part in _attach_closers([x for x in re.split(r'(?<=[，、；：])', s) if x.strip()]):
            if len(cur) + len(part) <= width:
                cur += part
            else:
                if cur:
                    lines.append(cur)
                cur = part
    if cur:
        lines.append(cur)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default='', help='只抓這一部（書名）')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--force', action='store_true')
    args = ap.parse_args()

    targets = [w for w in WORKS if not args.only or w[0] == args.only]
    if not targets:
        raise SystemExit('--only 書名不在清單：%s' % args.only)

    report = []
    for book, work, note in targets:
        meta = (api('/works', {'work': work}).get('results') or [{}])[0]
        if not meta:
            print('✗ %s：CBETA 查無 %s' % (book, work))
            report.append((book, work, '查無 work'))
            continue
        jl = [int(x) for x in re.split(r'[, ]+', str(meta.get('juan_list') or '')) if x]
        api_chars = int(meta.get('cjk_chars') or 0)
        print('● %s（%s）%s卷｜CBETA 題名 %s｜%s 字'
              % (book, work, meta.get('juan'), meta.get('title'), api_chars))
        if args.dry_run:
            continue
        path = os.path.join(YUAN, book + '.txt')
        if os.path.exists(path) and not args.force:
            print('  已有 %s，跳過（--force 可重抓）' % os.path.relpath(path, B))
            report.append((book, work, '已存在，未重抓'))
            continue
        txt, n_han = render(book, work, meta, jl)
        io.open(path, 'w', encoding='utf-8', newline='\n').write(txt)
        ratio = (n_han / api_chars) if api_chars else 0
        lines = txt.count('\n')
        print('  → %s｜%d 行｜漢字 %d／CBETA %d（%.1f%%）'
              % (os.path.relpath(path, B), lines, n_han, api_chars, ratio * 100))
        report.append((book, work, 'OK %d 行 %d 漢字 %.1f%%'
                       % (lines, n_han, ratio * 100)))
        if ratio < 0.90:
            print('  ！漢字比偏低，請檢查解析')

    print()
    print('=== 摘要 ===')
    for book, work, st in report:
        print('%-24s %-7s %s' % (book, work, st))
    bad = [r for r in report if r[2].startswith('查無')]
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
