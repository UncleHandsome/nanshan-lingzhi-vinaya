# -*- coding: utf-8 -*-
"""建立第二輪「純找碴」材料：原文＋待審譯文（不含改前），並附 AUDIT_PROMPT。

用法：
  python -X utf8 _src/mk_audit_materials.py --src 測試/回歸11組_一審 --out 測試/回歸11組_二審
"""
import argparse
import io
import os

import materials_io as MI

import book_config as BC
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'

AUDIT_PROMPT = BC.REAUDIT_PROMPT

def book_of(path_or_text):
    return BC.book_of(path_or_text)


def render_audit(note='', dual='', long='', logic=None, prefix='', suffix='',
                 substantive='', extra=None):
    """組出再審提示詞：全部佔位符（含 dual／long／logic）一次填滿，不可死碼。

    prefix／suffix 供未來材料層插入段落；extra 可覆寫任何 note（preface/dangling/typo…）。
    """
    vals = dict(extra or {})
    vals.setdefault('book_note', note)
    vals.setdefault('dual_note', dual)
    vals.setdefault('long_note', long)
    vals.setdefault('logic_checklist', BC.LOGIC_CHECKLIST if logic is None else logic)
    if substantive:
        vals['substantive_style'] = substantive
    p = BC.render(BC.REAUDIT_PROMPT_TMPL, **vals)
    if prefix:
        p = prefix.rstrip() + '\n\n' + p
    if suffix:
        p = p.rstrip() + '\n\n' + suffix.lstrip()
    return p

NOTE_CHAO = '《行事鈔》《義鈔》為比丘律制，部別稱謂須與比丘眾相應'


def _strip_head_paren(s):
    s = (s or '').lstrip('】*：: \t\r\n')
    if s[:1] in ('（', '('):
        m = re.match(r'[（(][^）)]*[）)]\s*[：:*]*\s*\n?', s)
        if m and re.search(r'註|注|按|說明|沿用|未改|以下|全文|白話|修訂|完整', m.group(0)):
            s = s[m.end():]
    return s.lstrip('】*：: \t\r\n')


_MARK = 'PASS_A_KEEP_A'


def _from_jia(md_text):
    m = re.search(r'■ (?:疏文|記文|鈔文|律文|註文|序文)（譯本甲）\s*\n+(.+?)'
                  r'(?=\n+■ |\n+【|\Z)', md_text or '', re.S)
    return MI.from_jia(md_text)


def col3(rt):
    m = re.search(
        r'(?:^|\n)\s*[#*\s]*(?:第\s*)?(?:3|三)\s*(?:(?:欄\s*[｜|：:]|[.、．：:]|\*\*)\s*)*(?:修正後|修訂後|定稿|最終)(?:的)?譯文\**\s*[：:\s]*\n?',
        rt,
    )
    if m:
        body = _strip_head_paren(rt[m.end():])
    else:
        i = rt.rfind('修正後的譯文')
        if i < 0:
            _k = rt.rfind('修正')
            if _k < 0:
                _k = rt.rfind('分歧與裁決')
            _from = _k if _k >= 0 else 0
            mm = re.compile(r'(?m)^\s*【(?:疏文|記文|鈔文|律文|註文|序文)】').search(rt, _from)
            if mm:
                return re.sub(r'\n{3,}', '\n\n',
                              rt[mm.start():].lstrip('】*：: \t\r\n')).strip()
            raise ValueError('回覆檔找不到「修正後的譯文」欄位')
        body = rt[i + len('修正後的譯文'):].lstrip('：: \t')
        if body.startswith('\n'):
            body = body[1:]
    body = body.lstrip('】*：: \t\r\n')
    return re.sub(r'\n{3,}', '\n\n', _strip_head_paren(body)).strip()


def col3_safe(rt):
    try:
        body = col3(rt)
    except ValueError:
        return None
    _has_lab = re.search(r'【(?:疏文|記文|鈔文|律文|註文|序文)】', body)
    if MI.is_keep_a(body):
        return _MARK
    _looks_report = re.search(r'結論|分歧與裁決', body[:80])
    if _looks_report and not _has_lab:
        return None
    if len(re.sub(r'【(?:疏文|記文|鈔文|律文|註文|序文)】', '', body).strip()) < 1:
        return None
    return _strip_head_paren(body)


def _pick_tag(head, why):
    """從裁決欄「（甲優／乙優／非甲優…）」精確取捨，避免「非甲優」被誤判為採甲。"""
    m = re.search(r'[（(]([^）)]{0,80})[）)]', head or '')
    seg = m.group(1) if m else (why or '')[:80]
    if re.search(r'(?:非|不|未|無)\s*甲優|甲優\s*(?:否|非)|不採甲', seg):
        return '乙'
    if '甲優' in seg:
        return '甲'
    if re.search(r'(?:非|不|未|無)\s*乙優|乙優\s*(?:否|非)', seg):
        return '重修'
    if '乙優' in seg:
        return '乙'
    return '重修'


def divergence(rt):
    """取裁決回覆的第 2 欄（分歧與裁決），供審核／修訂參考。"""
    m = re.search(r'分歧與裁決[^\n]*\n(.+?)(?=\n[#*\s]*(?:3|三)[.、．：:]|\n[#*\s【]*(?:修正後|修訂後|定稿|最終)(?:的)?譯文|\Z)',
                  rt, re.S)
    if not m:
        return ''
    txt = re.sub(r'\n{3,}', '\n\n', m.group(1)).strip()
    return txt[:2000]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--force', action='store_true')

    args = ap.parse_args()

    src = os.path.join(B, args.src.replace('/', os.sep))
    out = os.path.join(B, args.out.replace('/', os.sep))
    rep = os.path.join(src, '回覆')
    os.makedirs(out, exist_ok=True)
    _rep = os.path.join(out, '回覆')
    if (os.path.isdir(_rep) and
            any(f.endswith('_回.txt') for f in os.listdir(_rep)) and
            not getattr(args, 'force', False)):
        print('（已中止）輸出目錄已有回覆，重產材料會造成資料錯位：', out)
        print('  若確定要重跑，請加 --force；或改用新的輸出目錄。')
        raise SystemExit(2)

    for f in os.listdir(out):
        if f.endswith(('.md', '.json')) and not f.startswith('索引'):
            os.remove(os.path.join(out, f))

    n = 0
    for fn in sorted(os.listdir(src)):
        if not fn.endswith('.md'):
            continue
        key = fn[:-3]
        t = io.open(os.path.join(src, fn), encoding='utf-8').read()
        rp = os.path.join(rep, key + '_回.txt')
        if not os.path.exists(rp):
            continue
        rt = io.open(rp, encoding='utf-8').read()
        md0 = MI.load(src, key) or {}
        book = md0.get('book') or ''
        if book not in BC.BOOKS:
            book = book_of(t) if not book else BC.book_of('（出處：《%s》）' % book)
        if book not in BC.BOOKS:
            book = book_of(t)
        cfg = BC.cfg(book)
        _labs = {u.get('lab') for u in (md0.get('units') or []) if u.get('lab')}
        _long = bool(md0.get('long') or '（本段前文）' in t or '（本段後文）' in t)

        md = MI.load(src, key) or {}
        md = MI.fill_mother(md, md.get('book') or book, t)
        srcs = [(u['lab'], u['orig']) for u in md.get('units', [])]
        pre = md.get('pre', '')
        post = md.get('post', '')
        ex = re.search(r'（出處：(.+?)）', t)

        body = col3_safe(rt)
        if body is None and re.search(r'PASS_A', rt):
            body = _from_jia(t)
        if body == _MARK:
            body = _from_jia(t)
        if body is None:
            print('  ⚠ 略過異常檔：', key)
            continue
        if book == '資持記':
            body = re.sub(r'(?m)^【鈔文】', '【記文】', body)
        # 動態 note：雙欄／長段／序跋／句末懸空／疑訛，只對命中風險的段落注入
        _notes = BC.notes_for(book, _labs, ''.join(s for _, s in srcs), body,
                              long=_long, key=key)
        prompt = render_audit(_notes['book_note'], _notes['dual_note'],
                              _notes['long_note'], extra=_notes)

        L = [prompt, '', '---', '', '（出處：%s）' % ((ex.group(1) if ex else '') or ('《%s》' % (book or '未知'))), '']
        if pre:
            L += ['【前文背景（僅供參考，嚴禁譯入正文）】', '', pre, '']
        L += ['【原文】', '']
        if book == '資持記':
            srcs = [('記文' if lab == '鈔文' else lab, s) for lab, s in srcs]
        for lab, s in srcs:
            L += ['■ %s（原文）' % lab, '', s.strip(), '']
        div = divergence(rt)
        if div:
            _brief = []
            for _ln in div.split('\n'):
                _s = _ln.strip()
                if not _s:
                    continue
                _s = re.sub(r'^\s*(?:[-*•]|\d+[.、．])?\s*', '', _s).replace('**', '')
                _m = re.match(r'(.*?｜裁決[^：:\n]{0,40}[：:])(.*)', _s)
                if not _m:
                    continue
                _head = _m.group(1)
                _why = _m.group(2)
                _tag = _pick_tag(_head, _why)
                _srcs = re.findall(r'《[^》]{2,20}》[^，。；\n]{0,16}', _why)
                _hint = ('（線索：' + '、'.join(_srcs[:2]) + '）') if _srcs else ''
                if _tag == '甲':
                    _brief.append(_head + '採甲' + _hint)
                else:
                    _brief.append(_head + '採' + _tag + '：' + _why.strip()[:800])
            if _brief:
                L += ['【裁決分歧參考（僅供參考，勿照抄）】', '', '\n'.join(_brief), '']
        _ep = os.path.join(src, '回覆', key + '_evid.json')
        if os.path.exists(_ep):
            try:
                _ev = json.load(io.open(_ep, encoding='utf-8'))
                _bits = []
                for _it in (_ev if isinstance(_ev, list) else [])[:2]:
                    _tx = re.sub(r'https?://\S+', '', (_it.get('text') or '')).strip()
                    if _tx:
                        _bits.append(_tx[:400])
                if _bits:
                    L += ['【裁決檢索摘錄（僅供參考，勿照抄）】', '', '\n'.join(_bits), '']
            except Exception:
                pass
        L += ['【待審譯文】', '', body, '']
        if md.get('packed'):
            L += ['【分段要求】本單元含多個短段，請按 [1][2]… 編號逐條核對；【必改硬傷】條目前請加註段號 [n]，'
                  '勿合併或增減條數。', '']
        if post:
            L += ['【後文背景（僅供參考，嚴禁譯入正文）】', '', post, '']
        if md.get('mother'):
            L += ['【所釋鈔文（僅供對照，嚴禁譯入正文）】', '', md['mother'], '']

        io.open(os.path.join(out, fn), 'w', encoding='utf-8').write('\n'.join(L))
        n += 1

    print('已產生 %d 份二審材料 → %s' % (n, args.out))


if __name__ == '__main__':
    main()
