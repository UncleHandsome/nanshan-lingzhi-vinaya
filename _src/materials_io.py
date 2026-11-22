# -*- coding: utf-8 -*-
"""材料資料層：以 JSON 傳遞，取代各腳本重複用正則爬 .md。"""
import io
import json
import os
import re


def write_json(outdir, key, data):
    os.makedirs(outdir, exist_ok=True)
    p = os.path.join(outdir, key + '.json')
    io.open(p, 'w', encoding='utf-8').write(
        json.dumps(data, ensure_ascii=False, indent=1))
    return p


def read_json(dirpath, key):
    p = os.path.join(dirpath, key + '.json')
    if not os.path.exists(p):
        return None
    try:
        return json.load(io.open(p, encoding='utf-8'))
    except Exception:
        return None


SRC_RE = re.compile(r'■ (疏文|記文|鈔文|律文|註文|序文)（原文）(?:\[\d+\])?\s*\n+(.+?)'
                    r'(?=\n+■ |\n+【(?:後文背景|待審譯文|裁決分歧參考|目前譯文|分段要求|所釋鈔文)|\Z)', re.S)
TR_RE = re.compile(r'■ (疏文|記文|鈔文|律文|註文|序文)（現譯）\s*\n+(.+?)'
                   r'(?=\n+■ |\n+【(?:後文背景|待審譯文|裁決分歧參考|目前譯文|分段要求|所釋鈔文)|\Z)', re.S)
PRE_RE = re.compile(r'【前文背景[^】]*】\s*\n+(.+?)\n+\n*(?:【本次待審單元】|【本次待譯單元】|【分段要求】|【原文】)', re.S)
POST_RE = re.compile(r'【後文背景[^】]*】\s*\n+(.+?)(?=\s*【所釋鈔文|\Z)', re.S)
EX_RE = re.compile(r'（出處：(.+?)）')


def parse_md(text):
    """從 .md 材料抽出結構（向後相容）。"""
    ex = EX_RE.search(text)
    pre = PRE_RE.search(text)
    post = POST_RE.search(text)
    units = []
    trs = dict(TR_RE.findall(text))
    for lab, orig in SRC_RE.findall(text):
        units.append({'lab': lab, 'orig': orig.strip(), 'tr': trs.get(lab, '').strip()})
    _bk = re.search(r'《([^》]+)》', ex.group(1)) if ex else None
    return {
        'book': _bk.group(1) if _bk else '',
        'ex': ex.group(1) if ex else '',
        'pre': pre.group(1).strip() if pre else '',
        'post': post.group(1).strip() if post else '',
        'units': units,
    }


def load(dirpath, key):
    """優先讀 JSON，沒有就回頭解析 .md。"""
    d = read_json(dirpath, key)
    if d:
        for _u in (d.get('units') or []):
            if _u.get('orig'):
                _u['orig'] = re.sub(r'[（(]\s*[）)]', '', _u['orig'])
        return d
    p = os.path.join(dirpath, key + '.md')
    if not os.path.exists(p):
        return None
    return parse_md(io.open(p, encoding='utf-8').read())


def from_jia(md_text):
    hits = re.findall(
        r'■ (疏文|記文|鈔文|律文|註文|序文)（譯本甲）\s*\n(.*?)(?=\n+■ |\n+【(?:後文背景|待審譯文|裁決分歧參考|目前譯文|分段要求|所釋鈔文)|\Z)',
        md_text or '', re.S)
    return '\n\n'.join('【%s】\n%s' % (lab, body.strip()) for lab, body in hits)


KEEP_A = 'PASS_A_KEEP_A'


def is_keep_a(body):
    s = (body or '').strip(' \t\r\n`*。.')
    if s == KEEP_A:
        return True
    if KEEP_A in s and len(s) <= 60:
        return True
    if re.fullmatch(r'(?:沿用|同甲|與甲同|沿用甲|沿用甲譯|沿用譯本甲|沿用譯本甲之譯文)[。.]?', s):
        return True
    if re.fullmatch(r'(?:PASS_A[：:]?\s*)?(?:沿用|同|與)?(?:譯本)?甲(?:譯|本)?(?:之譯文)?'
                    r'[，,]?\s*(?:無實質(?:修改|差異|錯誤))?[。.]?', s):
        return True
    if s in ('沿用', '沿用甲', '沿用甲譯', '沿用譯本甲', '同甲', '與甲同'):
        return True
    return bool(re.fullmatch(r'^[【\[（(]?\s*(?:PASS_A\s*[:：/／]?\s*)?(?:[（(【\[]\s*)?(?:沿用|同)?(?:譯本)?甲(?:譯|本)?\s*(?:[】\])）])?$', s))


def fill_mother(md, book, text=''):
    """舊批次或長段缺 mother 時，現場用所釋鈔文索引補上（僅《資持記》）。"""
    if not isinstance(md, dict) or md.get('mother') or book != '資持記':
        return md
    try:
        import mother_corpus as MC
        u = ''.join((x.get('orig') or '') for x in (md.get('units') or []))
        m = MC.chao_for(u or text)
        if m:
            md['mother'] = m
    except Exception:
        pass
    return md


def verdict(rt):
    """回傳 'FIX' / 'PASS' / 'ERROR'（審核成果判定，統一邏輯）。"""
    rt = rt or ''
    # 「不應 PASS，應判 FIX」這類否定式不得當成 PASS
    rt = re.sub(r'(?:不應|不該|不得|不宜|不可|不能|不|非|不是|未可|難以|勿|莫)\s*'
                r'(?:判為|判作|判定|判|列為|予|視為|視作|算作|作)?\s*'
                r'(?:PASS_A|PASS)(?![A-Za-z_])', '', rt)
    # 「無須 FIX，判定 PASS」這類否定式不得當成 FIX
    rt = re.sub(r'(?:無須|不需|不必|不用|不判|未判|非屬|免|無|非|勿|莫)\s*'
                r'(?:改判|列為|判為|作)?\s*FIX', '', rt)

    def _looks_empty(s):
        s = (s or '').strip().lstrip('*：: -')
        if not s:
            return True
        # 明確否定／無誤整詞先判，避免「無需修改」被「修」字短路成 FIX
        _s0 = re.sub(r'[（(][^）)]*[）)]', '', s).strip(' ，,。.；;：:')
        _m0 = re.match(
            r'^(?:均|皆|並|悉|經核)?(?:無(?:須|需)?(?:修改|修訂)?|沒有|暫無|未見|未發現|不用|不須)'
            r'(?:任何)?(?:硬傷|問題|必改|漏譯|錯漏|錯誤|誤)?(?:修改|修訂)?(?:之處)?',
            _s0)
        if _m0:
            _rest = _s0[_m0.end():].strip(' ，,。.；;：:')
            _rest = re.sub(r'^[／/、,，]?\s*(?:無(?:須|需)?(?:修改|修訂)?|沒有|未見|未發現|不用|不須)(?:漏譯|錯漏|錯誤|硬傷|問題|誤|修改|修訂)?', '', _rest)
            if not any(w in _rest for w in ('須', '應', '補', '刪', '改', '修', '缺', '漏', '誤', '錯')):
                return True
        if s in ('無需修改', '無須修改', '無必改', '正確無誤', '無硬傷', '無問題'):
            return True
        if any(w in s for w in ('須', '應', '補', '刪', '改', '修', '缺', '漏', '誤', '錯')):
            return False
        return False

    m = re.search(r'【結論】[\s\S]{0,100}?(PASS_A|PASS|FIX)', rt)
    if not m:
        _ms = list(re.finditer(r'(?m)^[#*\s\d.、]*結論[\s\S]{0,100}?(PASS_A|PASS|FIX)', rt))
        m = _ms[-1] if _ms else None
    if m:
        if m.group(1) == 'FIX':
            return 'FIX'
        h = re.search(r'【必改硬傷】\s*(.+?)(?=【(?:可斟酌微瑕|微瑕|附註|建議|備註)】|\n\s*\**\s*4[.、．]|\Z)', rt, re.S)
        if h:
            seg = h.group(1).lstrip(' 　\t\r\n*#：:-')
            seg = re.sub(r'^(?:本段|全段|本單元|本組)\s*', '', seg)
            seg = re.sub(r'^(?:本段|全段|本單元|本組|經核對[^，。；]{0,12})[，。；：]?\s*', '', seg)
            seg = re.sub(r'^(?:經核對[^，。；]{0,12}|經逐句核對[^，。；]{0,12}|譯文正確|無需修改|正確無誤)[，。；：]?\s*', '', seg)
            for _ in range(3):
                _n2 = re.sub(r'^[（(【][^）)】]{0,16}[）)】]', '', seg)
                _n2 = re.sub(r'^(?:\d+[.、．]|[一二三四][.、．])\s*', '', _n2)
                _n2 = _n2.lstrip(' 　\t\r\n*#：:-')
                if _n2 == seg:
                    break
                seg = _n2
            if seg and not _looks_empty(seg):
                return 'FIX'
        return 'PASS'
    m2 = re.search(r'【必改硬傷】\s*(.+?)(?=【(?:可斟酌微瑕|微瑕|附註|建議|備註)】|\Z)', rt, re.S)
    if m2:
        return 'PASS' if _looks_empty(m2.group(1)) else 'FIX'
    return 'ERROR'


def verify_verdict(rt):
    """VERIFY 回覆判定：'OK' / 'RETRY' / 'ERROR'。

    只認【結論】後 20 字內的 OK／RETRY；否定式（不 OK、勿判 OK）與未過原因不誤判。
    """
    s = re.sub(r'[`*_#]', '', rt or '')
    if not s.strip():
        return 'ERROR'
    m = re.search(r'【結論】\s*([^\n]{0,30})', s)
    seg = m.group(1) if m else ''
    if not seg:
        # 無【結論】時取第一個非空行
        _lines = [x.strip() for x in s.split('\n') if x.strip()]
        seg = _lines[0][:30] if _lines else ''
    seg = re.sub(r'(?:不|非|勿|莫|未)\s*(?:判|算|視為)?\s*OK', '', seg, flags=re.I)
    if re.search(r'RETRY|重跑|退回', seg, re.I):
        return 'RETRY'
    if re.search(r'\bOK\b', seg, re.I):
        return 'OK'
    # 退而求其次：全文只出現一種判定
    _has_retry = bool(re.search(r'\bRETRY\b', s, re.I))
    _has_ok = bool(re.search(r'\bOK\b', s, re.I))
    if _has_retry and not _has_ok:
        return 'RETRY'
    if _has_ok and not _has_retry:
        return 'OK'
    return 'ERROR'


def verify_reasons(rt):
    """取 VERIFY 回覆的【未過原因】（供併回修訂清單）。"""
    m = re.search(r'【未過原因】\s*(.+?)(?=\n【|\Z)', rt or '', re.S)
    if not m:
        return ''
    body = m.group(1).strip()
    if re.fullmatch(r'[`*\s]*(?:無|无|無。|无须|無須)[`*\s。]*', body):
        return ''
    return body
