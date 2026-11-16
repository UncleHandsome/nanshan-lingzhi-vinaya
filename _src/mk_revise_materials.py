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

REVISE_PROMPT = '你是南山律典譯文修訂編輯（本段所屬：{book_note}）。下面提供【原文】、【目前譯文】、【終審硬傷清單】（若有【裁決分歧參考】，一併供核對）。\n\n動手前須自行核對【原文】與前後背景：只依硬傷清單逐項局部修正，清單未提及之處一律照【目前譯文】保留（勿為修辭改動），修訂時亦嚴禁新增解說性圓括號。修正時須辨明古今異義，以自然現代正體白話落實清單要素；若清單判斷反將導致誤譯、漏譯、破壞文氣或違背體例，應駁回該項、維持原譯（若有【裁決分歧參考】且原譯法更準，得參照採回）。駁回時只保留原句，不得書寫任何理由、按語或說明括號。\n\n### 硬傷清單：\n{fixes}\n\n### 輸出（完整譯文，勿重貼原文、勿輸出清單）：\n{out_format}'

def _strip_head_paren(s):
    s = (s or '').lstrip('*：: \t\r\n')
    if s[:1] in ('（', '('):
        m = re.match(r'[（(][^）)]*[）)]\s*[：:*]*\s*\n?', s)
        if m and re.search(r'註|注|按|說明|沿用|未改|以下|全文|白話|修訂|完整', m.group(0)):
            s = s[m.end():]
    return s.lstrip('*：: \t\r\n')


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
                              rt[mm.start():].lstrip('*：: \t\r\n')).strip()
            raise ValueError('回覆檔找不到「修正後的譯文」欄位')
        body = rt[i + len('修正後的譯文'):].lstrip('：: \t')
        if body.startswith('\n'):
            body = body[1:]
    body = body.lstrip('*：: \t\r\n')
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
    m = re.search(r'【必改硬傷】(.+?)(?=【可斟酌微瑕】|\n\s*\**\s*4[.、．：:]|\Z)', rt, re.S)
    if m:
        return m.group(1).strip()
    _m2 = re.search(r'必改硬傷\**[:：]?\s*(.+?)(?=\n\s*\**\s*4[.、．：:]|\Z)', rt, re.S)
    return _m2.group(1).strip() if _m2 else ''


def book_of(path_or_text):
    return BC.book_of(path_or_text)


def divergence(rt):
    """取裁決回覆的第 2 欄（分歧與裁決），供審核／修訂參考。"""
    m = re.search(r'分歧與裁決[^\n]*\n(.+?)(?=\n[#*\s]*(?:3|三)[.、．：:]|\n\s*\**\s*修正後的譯文|\Z)',
                  rt, re.S)
    if not m:
        return ''
    txt = re.sub(r'\n{3,}', '\n\n', m.group(1)).strip()
    return txt[:2000]


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

    plan = {'FIX': [], 'PASS': []}
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
        plan[v].append(key)
        if v != 'FIX':
            continue

        path = os.path.join(r1, fn)
        t = io.open(path, encoding='utf-8').read()
        md0 = MI.load(r1, key) or {}
        book = md0.get('book') or book_of(path)
        cfg = BC.cfg(book)
        ex = re.search(r'（出處：(.+?)）', t)
        md = MI.load(r1, key) or {}
        pre = md.get('pre', '')
        post = md.get('post', '')
        srcs = [(u['lab'], u['orig']) for u in md.get('units', [])]
        _r1t = io.open(os.path.join(r1_rep, key + '_回.txt'), encoding='utf-8').read()
        a1 = col3_safe(_r1t)
        if a1 is None and re.search(r'PASS_A', _r1t):
            a1 = MI.from_jia(t)
        if MI.is_keep_a(a1):
            a1 = MI.from_jia(t)
        if a1 is None:
            print('  ⚠ 修訂回覆異常，略過：', key)
            continue


        fmt = BC.fmt_for(book, md.get('units'))
        prompt = (REVISE_PROMPT.replace('{fixes}', fixes_block(art))
                  .replace('{out_format}', fmt)
                  .replace('{book_note}', cfg.get('note', '') or book))
        # 微瑕不列入自動修訂（避免無工具階段被未證實疑慮帶偏）

        L = [prompt, '', '---', '', '（出處：%s）' % ((ex.group(1) if ex else '') or ('《%s》' % (book or '未知'))), '']
        if pre:
            L += ['【前文背景（僅供參考）】', '', pre, '']
        L += ['【原文】', '']
        for lab, s in srcs:
            L += ['■ %s（原文）' % lab, '', s.strip(), '']
        if md.get('packed'):
            L += ['【分段要求】本單元含多個短段，請逐條保留 [1][2]… 原編號與標籤順序，'
                  '勿合併、漏號或改動編號；正文子序數用一、二、（一）（二），嚴禁額外 [數字] 或 -／*／1. 項目符號。', '']
        L += ['【目前譯文】', '', a1, '']
        _r1p = os.path.join(r1_rep, key + '_回.txt')
        if not os.path.exists(_r1p):
            print('  ⚠ 缺裁決回覆，略過：', key)
            continue
        div = divergence(io.open(_r1p, encoding='utf-8').read())
        if div:
            _dv = div if len(div) <= 500 else div[:500] + '…'
            L += ['【裁決分歧（僅供參考）】', '', _dv, '']
        if post:
            L += ['【後文背景（僅供參考）】', '', post, '']

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
    print('已產生 %d 份修訂材料 → %s' % (n, args.out))


if __name__ == '__main__':
    main()
