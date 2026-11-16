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
                    r'(?=\n+■ |\n+【(?:後文背景|待審譯文|裁決分歧參考|目前譯文|分段要求)|\Z)', re.S)
TR_RE = re.compile(r'■ (疏文|記文|鈔文|律文|註文|序文)（現譯）\s*\n+(.+?)'
                   r'(?=\n+■ |\n+【(?:後文背景|待審譯文|裁決分歧參考|目前譯文|分段要求)|\Z)', re.S)
PRE_RE = re.compile(r'【前文背景[^】]*】\s*\n+(.+?)\n+\n*(?:【本次待審單元】|【本次待譯單元】|【分段要求】|【原文】)', re.S)
POST_RE = re.compile(r'【後文背景[^】]*】\s*\n+(.+?)\s*\Z', re.S)
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
    return {
        'ex': ex.group(1) if ex else '',
        'pre': pre.group(1).strip() if pre else '',
        'post': post.group(1).strip() if post else '',
        'units': units,
    }


def load(dirpath, key):
    """優先讀 JSON，沒有就回頭解析 .md。"""
    d = read_json(dirpath, key)
    if d:
        return d
    p = os.path.join(dirpath, key + '.md')
    if not os.path.exists(p):
        return None
    return parse_md(io.open(p, encoding='utf-8').read())


def from_jia(md_text):
    hits = re.findall(
        r'■ (疏文|記文|鈔文|律文|註文|序文)（譯本甲）\s*\n+(.+?)(?=\n+■ |\n+【(?:後文背景|待審譯文|裁決分歧參考|目前譯文|分段要求)|\Z)',
        md_text or '', re.S)
    return '\n\n'.join('【%s】\n%s' % (lab, body.strip()) for lab, body in hits)


KEEP_A = 'PASS_A_KEEP_A'


def is_keep_a(body):
    s = (body or '').strip(' \t\r\n`*。.')
    if s == KEEP_A:
        return True
    if KEEP_A in s and len(s) <= 60:
        return True
    return bool(re.fullmatch(r'[【\[（(]?\s*沿用譯本甲\s*[】\]）)]?', s))


def verdict(rt):
    """回傳 'FIX' 或 'PASS'（審核成果判定，統一邏輯）。"""
    rt = rt or ''
    m = re.search(r'【結論】[^A-Za-z]{0,40}(PASS_A|PASS|FIX)', rt)
    if not m:
        _ms = list(re.finditer(r'(?m)^[#*\s\d.、]*結論[^A-Za-z]{0,40}(PASS_A|PASS|FIX)', rt))
        m = _ms[-1] if _ms else None
    if m:
        if m.group(1) == 'FIX':
            return 'PASS' if re.search(r'無\s*FIX|沒有\s*FIX|非\s*FIX', rt) else 'FIX'
        # 結論 PASS 但硬傷欄有內容 → 從嚴判 FIX，避免漏改
        h = re.search(r'【必改硬傷】\s*(.{0,300}?)(?=【可斟酌微瑕】|\n\s*\**\s*4[.、．]|\Z)', rt, re.S)
        if h:
            seg = h.group(1).lstrip(' 　\t\r\n*#：:-')
            seg = re.sub(r'^(?:本段|全段|本單元|本組)\s*', '', seg)
            seg = re.sub(r'^(?:經核對[^，。；]{0,12}|經逐句核對[^，。；]{0,12}|譯文正確|無需修改|正確無誤)[，。；：]?\s*', '', seg)
            for _ in range(3):
                _n2 = re.sub(r'^[（(【][^）)】]{0,16}[）)】]', '', seg)
                _n2 = re.sub(r'^(?:\d+[.、．]|[一二三四][.、．])\s*', '', _n2)
                _n2 = _n2.lstrip(' 　\t\r\n*#：:-')
                if _n2 == seg:
                    break
                seg = _n2
            if seg and not seg.startswith(('無', '暫無', '沒有', 'none', 'None', '皆無', '經核無',
                                 '查無', '並無', '未發現', '未見', '均無', '悉無', '無任何', '無硬傷', '無必改', '無需修改', '正確無誤')):
                return 'FIX'
        return 'PASS'
    m2 = re.search(r'【必改硬傷】\s*(.{0,40})', rt, re.S)
    if m2 and not m2.group(1).strip().lstrip('*：: -').startswith('無'):
        return 'FIX'
    return 'PASS'
