# -*- coding: utf-8 -*-
"""二審後處理：PASS 直接沿用一審；FIX 產生「定點修訂」材料以產出 A2。

用法：
  python -X utf8 _src/mk_revise_materials.py --out 測試/回歸11組_A2
"""
import argparse
import io
import json
import os

import materials_io as MI

import book_config as BC
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'

REVISE_PROMPT = BC.REVISE_PROMPT

def book_of(path_or_text):
    return BC.book_of(path_or_text)

    s = (s or '').lstrip('】*：: \t\r\n')
    if s[:1] in ('（', '('):
        m = re.match(r'[（(][^）)]*[）)]\s*[：:*]*\s*\n?', s)
        if m and re.search(r'註|注|按|說明|沿用|未改|以下|全文|白話|修訂|完整', m.group(0)):
            s = s[m.end():]
    return s.lstrip('】*：: \t\r\n')


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
    _looks_report = re.search(r'結論|分歧與裁決', body[:80])
    if _looks_report and not _has_lab:
        return None
    if len(re.sub(r'【(?:疏文|記文|鈔文|律文|註文|序文)】', '', body).strip()) < 1:
        return None
    return _strip_head_paren(body)


def verdict(rt):
    return MI.verdict(rt)


def fixes_block(rt):
    _pre = ''

    m = re.search(r'【必改硬傷】(.+?)(?=【可斟酌微瑕】|\n\s*\**\s*4[.、．：:]|\Z)', rt, re.S)
    if m:
        return _pre + m.group(1).strip()
    _m2 = re.search(r'必改硬傷\**[:：]?\s*(.+?)(?=\n\s*\**\s*4[.、．：:]|\Z)', rt, re.S)
    return _pre + _m2.group(1).strip() if _m2 else ''


def book_of(path_or_text):
    return BC.book_of(path_or_text)


def divergence(rt):
    """取裁決回覆的第 2 欄（分歧與裁決），供審核／修訂參考。"""
    m = re.search(r'分歧與裁決[^\n]*\n(.+?)(?=\n[#*\s]*(?:3|三)[.、．：:]|\n[#*\s【]*(?:修正後|修訂後|定稿|最終)(?:的)?譯文|\Z)',
                  rt, re.S)
    if not m:
        return ''
    txt = re.sub(r'\n{3,}', '\n\n', m.group(1)).strip()
    return txt[:2000]


def _evid_plain(s):
    return re.sub(r'[^\u4e00-\u9fffA-Za-z0-9]', '', s or '')


def evidence_block(aud_rep, key, fixes_txt, max_chars=2200):
    """讀 *_evid.json，挑與硬傷相關的片段；網搜證據優先（修訂階段 NO_WEB=0、web_search 至多 1 次）。"""
    ep = os.path.join(aud_rep, key + '_evid.json')
    if not os.path.exists(ep):
        return ''
    try:
        items = json.load(io.open(ep, encoding='utf-8'))
    except Exception:
        return ''
    if not isinstance(items, list) or not items:
        return ''

    _ev_refs = [_evid_plain(x) for x in re.findall(r'依據[：:]\s*([^\n｜]+)', fixes_txt or '')]
    quotes = [_evid_plain(q) for q in re.findall(r'[「『]([^」』]{2,80})[」』]', fixes_txt or '')]
    quotes = [q for q in (quotes + _ev_refs) if len(q) >= 2]
    fix_plain = _evid_plain(fixes_txt)

    scored = []
    for idx, it in enumerate(items):
        raw_txt = re.sub(r'https?://\S+', '', (it.get('text') or '')).strip()
        if not raw_txt:
            continue
        bk = (it.get('book') or '').strip()
        src = it.get('src') or 'local'
        tp = _evid_plain(raw_txt)
        sc = 0
        if src in ('web_search', 'web_fetch'):
            sc += 3
        if bk and (_evid_plain(bk) in fix_plain or (len(bk) >= 2 and bk[:2] in (fixes_txt or ''))):
            sc += 5
        for q in quotes:
            if q in tp:
                sc += 10
            elif len(q) >= 4:
                grams = {q[i:i + 3] for i in range(len(q) - 2)}
                sc += sum(1 for g in grams if g in tp)
        scored.append((sc, -idx, it, raw_txt))

    scored.sort(reverse=True)
    has_hit = any(sc >= 5 for sc, _, _, _ in scored)
    if not has_hit:
        return ''
    budget = max_chars
    limit_n = len(scored) if has_hit else 2

    lines, acc = [], 0
    for sc, _, it, raw_txt in scored[:limit_n]:
        src = it.get('src') or 'local'
        bk = (it.get('book') or '').strip()
        jn = (it.get('juan') or '').strip()
        q = (it.get('q') or '').strip()
        if src == 'local':
            tag = '本地｜《%s》%s｜查「%s」' % (bk or '未名', jn, q)
            cap = 480
        else:
            tag = '網搜｜%s｜查「%s」' % (bk or '白名單', q)
            cap = 650
        if len(raw_txt) <= cap:
            body = raw_txt
        elif src == 'web_fetch':
            _mid = len(raw_txt) // 2
            _st = max(0, _mid - cap // 2)
            body = ('…' if _st else '') + raw_txt[_st:_st + cap] + '…'
        else:
            body = raw_txt[:cap] + '…'
        row = '- [%s] %s' % (tag, body.replace('\n', ' '))
        if acc + len(row) > budget and lines:
            break
        lines.append(row)
        acc += len(row) + 1
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--r1', default='測試/回歸11組_一審')
    ap.add_argument('--audit', default='測試/回歸11組_二審')
    ap.add_argument('--out', required=True)
    ap.add_argument('--force', action='store_true')

    args = ap.parse_args()

    r1 = os.path.join(B, args.r1.replace('/', os.sep))
    au = os.path.join(B, args.audit.replace('/', os.sep))
    out = os.path.join(B, args.out.replace('/', os.sep))
    aud_rep = os.path.join(au, '回覆')
    r1_rep = os.path.join(r1, '回覆')
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

    plan = {'FIX': [], 'PASS': [], 'ERROR': []}
    n = 0
    for fn in sorted(os.listdir(r1)):
        if not fn.endswith('.md'):
            continue
        key = fn[:-3]
        ap_ = os.path.join(aud_rep, key + '_回.txt')
        if not os.path.exists(ap_):
            continue
        art = io.open(ap_, encoding='utf-8').read()
        v = verdict(art)
        if v not in plan:
            v = 'ERROR'
            print('  ⚠ 終審回覆結構異常（ERROR）：', key)
        plan[v].append(key)
        if v != 'FIX':
            continue

        path = os.path.join(r1, fn)
        t = io.open(path, encoding='utf-8').read()
        md0 = MI.load(r1, key) or {}
        book = md0.get('book') or book_of(path)
        _bm = re.search(r'（出處：《([^》]+)》', t)
        if _bm:
            book = BC.book_of('（出處：《%s》）' % _bm.group(1)) or book
        if book not in BC.BOOKS:
            book = book_of(path)
        cfg = BC.cfg(book)
        ex = re.search(r'（出處：(.+?)）', t)
        md = MI.load(r1, key) or {}
        md = MI.fill_mother(md, book, t)
        pre = md.get('pre', '')
        post = md.get('post', '')
        srcs = [(u['lab'], u['orig'], u.get('pack_idx')) for u in md.get('units', [])]
        _r1p = os.path.join(r1_rep, key + '_回.txt')
        if os.path.abspath(r1) != os.path.abspath(au) and os.path.exists(_r1p):
            _r1t = io.open(_r1p, encoding='utf-8').read()
        else:
            _mdp = os.path.join(r1, key + '.md')
            _r1t = ''
            if os.path.exists(_mdp):
                _mt = io.open(_mdp, encoding='utf-8').read()
                _i = _mt.rfind('【待審譯文】')
                if _i >= 0:
                    _seg = _mt[_i + len('【待審譯文】'):]
                    _cand = [x for x in (_seg.find('\n【後文背景'), _seg.find('\n【所釋鈔文')) if x > 0]
                    _j = min(_cand) if _cand else -1
                    if _j > 0:
                        _seg = _seg[:_j]
                    _r1t = '【修正後的譯文】\n' + _seg.strip()
        if not _r1t:
            print('  ⚠ 缺裁決回覆且無待審譯文，略過：', key)
            continue
        a1 = col3_safe(_r1t)
        if a1 is None and re.search(r'PASS_A', _r1t):
            a1 = MI.from_jia(t)
        if MI.is_keep_a(a1):
            a1 = MI.from_jia(t)
        if a1 is None:
            print('  ⚠ 修訂回覆異常，略過：', key)
            continue


        if book == '資持記':
            srcs = [('記文' if lab == '鈔文' else lab, s, _pi) for lab, s, _pi in srcs]
            a1 = re.sub(r'(?m)^【鈔文】', '【記文】', a1)
            for _u in (md.get('units') or []):
                if _u.get('lab') == '鈔文':
                    _u['lab'] = '記文'
        _labs = {u.get('lab') for u in (md.get('units') or []) if u.get('lab')}
        _note = BC.note_for(book, _labs)
        if md.get('packed'):
            _ordered_labs = list(dict.fromkeys(u.get('lab') for u in (md.get('units') or []) if u.get('lab')))
            if len(md.get('members') or []) > 1:
                _inner = '\n'.join('【%s】……' % l for l in (_ordered_labs or [cfg['unit']]))
                fmt = '[1]\n%s\n[2]\n%s\n（依各條原有標籤結構與原編號逐條完整輸出）' % (_inner, _inner)
            else:
                _only_lab = (_ordered_labs[0] if _ordered_labs else cfg['unit'])
                fmt = '【%s】\n[1] ……\n[2] ……（標籤僅寫開頭一次，依原編號逐條完整輸出）' % _only_lab
        else:
            fmt = BC.fmt_for(book, md.get('units'))
        fixes_txt = fixes_block(art)
        prompt = BC.revise_prompt(
            book, _note, _labs, ''.join(s for _, s, _pi in srcs), a1,
            long=bool(md.get('long')), key=key, fixes=fixes_txt, out_format=fmt)
        # 微瑕不列入自動修訂（避免無工具階段被未證實疑慮帶偏）

        L = [prompt, '', '---', '', '（出處：%s）' % ((ex.group(1) if ex else '') or ('《%s》' % (book or '未知'))), '']
        if pre:
            L += ['【前文背景（僅供參考，嚴禁譯入正文）】', '', pre, '']
        L += ['【原文】', '']
        for lab, s, _pi in srcs:
            _sfx = ('[%d]' % _pi) if _pi else ''
            L += ['■ %s（原文）%s' % (lab, _sfx), '', s.strip(), '']
        if md.get('packed'):
            if len(md.get('members') or []) > 1:
                L += ['【分段要求】本單元含多個短段，請逐條保留 [1][2]… 原編號與各條內原有的標籤結構，'
                      '勿合併、漏號或刪改標籤位置；嚴禁額外 [數字]（會與分段編號混淆）。', '']
            else:
                L += ['【分段要求】本單元含多個短段，請逐條保留 [1][2]… 原編號與標籤順序，'
                      '勿合併、漏號或改動編號；欄位標籤只需寫在最開頭一次，勿在每個編號前重複；嚴禁額外 [數字]（會與分段編號混淆）。', '']
        L += ['【目前譯文】', '', a1, '']
        _r1p = os.path.join(r1_rep, key + '_回.txt')
        div = divergence(_r1t)
        if '長段拼回定稿' in div:
            div = ''
        if div:
            _dv = div if len(div) <= 2000 else div[:2000].rsplit('\n', 1)[0] + '\n…（以下省略）'
            L += ['【裁決分歧參考】', '', _dv, '']
        ev = evidence_block(aud_rep, key, fixes_txt)
        if ev:
            L += ['【初審檢索摘錄（僅供核對依據，嚴禁抄入譯文）】', '', ev, '']
        if post:
            L += ['【後文背景（僅供參考，嚴禁譯入正文）】', '', post, '']
        if md.get('mother'):
            L += ['【所釋鈔文（僅供對照，嚴禁譯入正文）】', '', md['mother'], '']

        n += 1
        io.open(os.path.join(out, key + '.md'), 'w', encoding='utf-8').write('\n'.join(L))

    order = {k: i + 1 for i, k in enumerate(
        sorted([x[:-3] for x in os.listdir(r1) if x.endswith('.md')]))}
    json.dump({'order': order, 'FIX': plan['FIX'], 'PASS': plan['PASS'],
               'materials': n},
              io.open(os.path.join(out, '索引.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('FIX %d 組：%s' % (len(plan['FIX']), plan['FIX']))
    print('PASS %d 組：%s' % (len(plan['PASS']), plan['PASS']))
    print('ERROR %d 組（未計入修訂）：%s' % (len(plan['ERROR']), plan['ERROR']))
    print('已產生 %d 份修訂材料 → %s' % (n, args.out))


if __name__ == '__main__':
    main()
