# -*- coding: utf-8 -*-
"""由修訂回覆組出定稿：支援指定底本、二審、修訂目錄。

用法：
  python -X utf8 _src/build_a2.py --base 測試/批次_裁決 --audit 測試/批次_終審 \
      --revise 測試/批次_終修 --out 測試/批次_Final
"""
import argparse
import io
import json
import os
import re

import norm
import materials_io as MI

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'


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


def _plain_revise(rt):
    txt = (rt or '').strip()
    _mh = re.search(r'(?m)^\s*(?:#+\s*)?(?:3[.、]\s*)?(?:\*\*)?\s*(?:修正後|修訂後|修正|修訂)(?:的)?譯文', txt)
    i = _mh.start() if _mh else -1
    if i >= 0:
        _end = _mh.end() if _mh else i + 6
        txt = txt[_end:].lstrip('】*：: \t\r\n')
    else:
        _m = re.search(r'【(?:疏文|記文|鈔文|律文|註文|序文)】', txt)
        if _m:
            txt = txt[_m.start():]
    return _strip_head_paren(txt).strip()


def col3(rt):
    m = re.search(
        r'(?:^|\n)\s*[#*\s]*(?:第\s*)?(?:3|三)\s*(?:(?:欄\s*[｜|：:]|[.、．：:]|\*\*)\s*)*(?:修正後|修訂後|定稿|最終)(?:的)?譯文\**\s*[：:\s]*\n?',
        rt)
    if m:
        body = _strip_head_paren(rt[m.end():].lstrip('】*：: \t\r\n'))
        if body:
            return re.sub(r'\n{3,}', '\n\n', _strip_head_paren(body)).strip()
    i = rt.rfind('修正後的譯文')
    if i >= 0:
        body = _strip_head_paren(rt[i + len('修正後的譯文'):].lstrip('】*：: \t\r\n'))
        if body:
            return re.sub(r'\n{3,}', '\n\n', _strip_head_paren(body)).strip()
    _k = rt.rfind('分歧與裁決')
    _from = _k if _k >= 0 else 0
    mm = re.compile(r'(?m)^\s*【(?:疏文|記文|鈔文|律文|註文|序文)】').search(rt, _from)
    if mm:
        return re.sub(r'\n{3,}', '\n\n', rt[mm.start():].lstrip('】*：: \t\r\n')).strip()
    raise ValueError('找不到「修正後的譯文」欄位')


def col3_soft(rt):
    try:
        body = col3(rt)
    except Exception:
        return None
    _has_lab = re.search(r'【(?:疏文|記文|鈔文|律文|註文|序文)】', body)
    _looks_report = re.search(r'結論|分歧與裁決', body[:80])
    if _looks_report and not _has_lab:
        return None
    if len(re.sub(r'【(?:疏文|記文|鈔文|律文|註文|序文)】', '', body).strip()) < 1:
        return None
    return _strip_head_paren(body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', required=True, help='底本批次（含 回覆/）')
    ap.add_argument('--audit', required=True, help='終審批次（含 回覆/）')
    ap.add_argument('--revise', required=True, help='修訂批次（含 回覆/）')
    ap.add_argument('--blind', default='', help='盲翻批次（補位用）')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    base = os.path.join(B, args.base.replace('/', os.sep))
    audit = os.path.join(B, args.audit.replace('/', os.sep))
    revise = os.path.join(B, args.revise.replace('/', os.sep))
    blind = os.path.join(B, args.blind.replace('/', os.sep)) if args.blind else ''
    out = os.path.join(B, args.out.replace('/', os.sep))
    os.makedirs(out, exist_ok=True)

    keys = sorted(f[:-3] for f in os.listdir(base) if f.endswith('.md'))
    for _f in os.listdir(out):
        if _f.endswith('.txt') and _f[:-4] not in keys:
            try:
                os.remove(os.path.join(out, _f))
            except Exception:
                pass
    fix = pass_ = 0
    missing = []
    unaudited = []
    unfixed = []
    over = []
    for key in keys:
        ap_ = os.path.join(audit, '回覆', key + '_回.txt')
        rp = os.path.join(revise, '回覆', key + '_回.txt')
        bp = os.path.join(base, '回覆', key + '_回.txt')
        is_fix = False
        if not os.path.exists(ap_):
            unaudited.append(key)
            continue
        else:
            v = io.open(ap_, encoding='utf-8').read()
            _vd = MI.verdict(v)
            if _vd == 'ERROR':
                unaudited.append(key)
                continue
            is_fix = _vd == 'FIX'
        if is_fix and os.path.exists(rp):
            _rt = io.open(rp, encoding='utf-8').read()
            try:
                txt = col3(_rt) if re.search(r'(?:修正後|修訂後|定稿|最終)(?:的)?譯文', _rt) else None
            except Exception:
                txt = None
            if not txt:
                _md = MI.load(base, key) or {}
                _lab0 = next((u.get('lab') for u in (_md.get('units') or []) if u.get('lab')), '')
                _rt0 = re.sub(r'【(?:修訂後的譯文|修訂後譯文|修訂譯文|修正後的譯文|修正譯文)】', '', _rt)
                txt = _plain_revise(_rt0)
                if _lab0 and not re.search(r'【(?:疏文|記文|鈔文|律文|註文|序文)】', txt or ''):
                    txt = '【%s】\n' % _lab0 + (txt or '')
            if txt is not None:
                txt = _strip_head_paren(txt).strip()
                txt = re.sub(r'[（(](?:按|註|注|駁回|維持原譯|校按|修訂說明|說明|備註)[：:][^）)]*[）)]\s*(?=\n|$)', '', txt).strip()
                txt = re.sub(r'[（(](?:按|駁回|維持原譯|校按|修訂說明)[：:][^）)]*[）)]\s*(?=\n|$)', '', txt).strip()
            if not txt or len(txt.strip()) < 1:
                txt = None
            if txt is None and os.path.exists(bp):
                txt = col3_soft(io.open(bp, encoding='utf-8').read())
                if MI.is_keep_a(txt):
                    _bm2 = os.path.join(base, key + '.md')
                    if os.path.exists(_bm2):
                        txt = MI.from_jia(io.open(_bm2, encoding='utf-8').read())
                if txt is not None:
                    unfixed.append(key)
            if not txt or not str(txt).strip():
                missing.append(key)
                continue
            if key not in unfixed:
                fix += 1
                if os.path.exists(bp):
                    _old_txt = col3_soft(io.open(bp, encoding='utf-8').read()) or ''
                    if MI.is_keep_a(_old_txt):
                        _old_txt = MI.from_jia(io.open(os.path.join(base, key + '.md'), encoding='utf-8').read()) or ''
                    _ob = len(re.sub(r'\s', '', _old_txt))
                    _nb = len(re.sub(r'\s', '', txt or ''))
                    if _ob and (_nb > _ob * 1.25 or _nb < _ob * 0.7):
                        over.append('%s\t%d→%d' % (key, _ob, _nb))
                        io.open(os.path.join(out, '_修訂幅度警報.log'), 'a', encoding='utf-8').write(
                            '%s\t%d→%d\n' % (key, _ob, _nb))
        else:
            if not os.path.exists(bp):
                missing.append(key)
                continue
            if is_fix:
                print('  ⚠ FIX 缺修訂檔，改用裁決稿（未修訂）：', key)
                unfixed.append(key)
            txt = col3_soft(io.open(bp, encoding='utf-8').read())
            if MI.is_keep_a(txt):
                _bm = os.path.join(base, key + '.md')
                if os.path.exists(_bm):
                    txt = MI.from_jia(io.open(_bm, encoding='utf-8').read())
            _is_passa = False
            if os.path.exists(bp):
                _jt = io.open(bp, encoding='utf-8').read()
                _pm = re.search(r'結論[^A-Za-z]{0,12}(PASS_A|REVISED)', _jt)
                _is_passa = bool(_pm and _pm.group(1) == 'PASS_A')
            if txt is None:
                _kt = _jt if os.path.exists(bp) else ''
                _k = _kt.rfind('分歧與裁決')
                _mm = re.compile(r'(?m)^\s*【(?:疏文|記文|鈔文|律文|註文|序文)】').search(_kt, _k if _k >= 0 else 0)
                if _mm:
                    txt = _kt[_mm.start():].strip()
                    print('  ↺ 裁決缺標題，改用第 3 欄標籤起段：', key)
            if txt is None and blind and _is_passa:
                _bl = os.path.join(blind, '回覆', key + '_回.txt')
                if os.path.exists(_bl):
                    txt = io.open(_bl, encoding='utf-8').read().strip()
                    print('  ↺ 裁決缺譯文，改用盲翻稿：', key)
            if not txt or not str(txt).strip():
                missing.append(key)
                continue
            pass_ += 1
        _md_chk = MI.load(base, key) or {}
        if _md_chk.get('packed'):
            _need = len(_md_chk.get('segments') or []) or len(_md_chk.get('members') or [])
            _chk = re.sub(r'(?m)^【(?:疏文|記文|鈔文|律文|註文|序文)】\s*', '', txt or '')
            _nums = [int(n) for n in re.findall(r'(?m)^\s*\[\s*(\d+)\s*\]', _chk)]
            if _need and _nums != list(range(1, _need + 1)):
                print('  ✗ 打包段編號不完整（需 1..%d，得 %s）：%s' % (_need, sorted(set(_nums)), key))
                missing.append(key)
                continue
        _labs_exp = {u.get('lab') for u in (_md_chk.get('units') or []) if u.get('lab')}
        if (_md_chk.get('book') == '資持記' or '資持記' in str(base)) and _labs_exp == {'鈔文'}:
            _labs_exp = {'記文'}
        _got = set(re.findall(r'【(疏文|記文|鈔文|律文|註文|序文)】', txt))
        if len(_labs_exp) == 1 and not _got:
            _only = next(iter(_labs_exp))
            txt = '【%s】\n' % _only + txt
            _got = {_only}
        if len(_labs_exp) == 1 and _got and _got != _labs_exp:
            # 修訂模型自創標籤（如【修訂譯文】）經 norm 轉成預設【鈔文】時，改回本段應有標籤
            _only = next(iter(_labs_exp))
            txt = re.sub(r'【(?:疏文|記文|鈔文|律文|註文|序文)】', '【%s】' % _only, txt, count=1)
            _got = {_only}
        _extra = _got - _labs_exp
        if _extra:
            print('  ✗ 譯文多出非本段欄位（%s），不寫入定稿：%s' % ('／'.join(sorted(_extra)), key))
            missing.append(key)
            continue
        if len(_labs_exp) > 1:
            _lack = sorted(_labs_exp - _got)
        elif _got:
            _lack = sorted(_labs_exp - _got)
        else:
            _lack = []
        if _lack:
            print('  ✗ 譯文缺欄（%s），不寫入定稿：%s' % ('／'.join(_lack), key))
            missing.append(key)
            continue
        if re.search(r'(?:local_search|web_search|web_fetch)\s*\(', txt):
            print('  ⚠ 含工具呼叫字面，判為異常：', key)
            missing.append(key)
            continue
        _src_txt = ''.join((u.get('orig') or '') for u in (_md_chk.get('units') or []))
        io.open(os.path.join(out, key + '.txt'), 'w', encoding='utf-8').write(norm.normalize(txt, _src_txt))

    print('定稿：FIX %d、沿用 %d、缺 %d、未審核 %d、未修訂 %d、幅度異常 %d → %s'
          % (fix, pass_, len(missing), len(unaudited), len(unfixed), len(over), args.out))
    for name, lst in (('_未審核清單.log', unaudited), ('_未修訂清單.log', unfixed),
                      ('_未完成清單.log', over)):
        if lst:
            io.open(os.path.join(out, name), 'w', encoding='utf-8').write('\n'.join(lst))
    if missing:
        print('  缺：', missing[:10])
    json.dump({'base': args.base, 'audit': args.audit, 'revise': args.revise,
               'fix': fix, 'pass': pass_, 'missing': missing,
               'unaudited': unaudited, 'unfixed': unfixed, 'over': over},
              io.open(os.path.join(out, '索引.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    if missing or unaudited or unfixed or over:
        print('  有缺檔／未審核／未修訂／修訂幅度異常，回傳非零')
        raise SystemExit(1)


if __name__ == '__main__':
    main()
