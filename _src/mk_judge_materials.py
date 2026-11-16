# -*- coding: utf-8 -*-
"""路線③ 步驟2：差分裁決材料（原文 ‖ 譯本A ‖ 譯本B）。

用法：
  # A = 現譯（材料內建）
  python -X utf8 _src/mk_judge_materials.py --src 測試/回歸11組 \
      --a 測試/回歸11組_盲翻/回覆 --b out --out 測試/回歸11組_裁決A0

  # A = 第一輪修正
  python -X utf8 _src/mk_judge_materials.py --src 測試/回歸11組 \
      --a 測試/回歸11組_一審/回覆 --b 測試/回歸11組_盲翻/回覆 --out 測試/回歸11組_裁決A1
"""
import argparse
import shutil
import io
import os

import materials_io as MI
import norm

import book_config as BC
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'

JUDGE_PROMPT = '你是南山律典雙譯裁決編輯。同一段原文附有【譯本甲】（主底本）與【譯本乙】（對照）。\n\n只針對【本次待審單元】中立比對原文與前後背景，切勿把前後背景譯入正文，亦勿因看似流暢或已有括注而盲目偏袒任一方。\n\n### 原則\n1. **依原文與律脈裁定**（{book_note}）：主客施受、開遮模態、範圍與否定作用域、句尾虛字斷句、引文與評論邊界、古今與同形異義、數理度量（保留原稱）、科判層級與「文」之所指；分清本宗《四分》定論與他部異說。除原文實質夾注與讀音釋義外，不用圓括號添加解說（必要之省略主賓或前提條件直接融入正句）。\n2. **防範同誤**：即使甲、乙譯法一致，仍須獨立對照原文核驗，防範共同漏譯、施受反轉、誤斷句讀或文言直抄。\n3. **最小改動與體例一致**：有實質修正或防同誤重修者判 `REVISED`，未列分歧之句照甲保留，所有改動處皆須列入第 2 欄，且第 3 欄須嚴格貫徹第 2 欄之取捨，勿殘留雙譯並存或同義疊詞；實質無誤且僅純修辭差異者判 `PASS_A`。\n\n### 輸出\n1. **結論**：`PASS_A` 或 `REVISED`\n2. **分歧與裁決**：PASS_A 寫「沿用譯本甲」或「乙有誤：……；甲優」；REVISED 逐條寫 `[疏/記/鈔/律/註/序，打包段加[n]] 原文「……」｜甲作「……」vs 乙作「……」（或甲乙同作「……」）｜裁決（甲優／乙優／重修）：……`\n3. **修正後的譯文**：PASS_A 時只寫一行 `PASS_A_KEEP_A`（勿加括號）；REVISED 時完整輸出，須照原樣以原標籤開頭，嚴禁自創標籤（若材料附【分段要求】，依其規定只列改動段號）：\n{out_format}'

NOTE_NICAO = ('《比丘尼鈔》須依比丘尼律制與對舉「僧／尼」語境審斷；'
              '檢索《行事鈔》等平行文對讀時，須尊重《尼鈔》對尼眾之改制與節略，'
              '不得以比丘制硬套覆蓋')
NOTE_SHUJI = ('《業疏》「文／注」指《隨機羯磨》，《戒疏》「文／注」指《含注戒本》，'
              '「律」方指《四分律》；記文之「疏云／鈔云／文云／注云」須依所釋之書判讀，'
              '且【疏】【記】須義理相契')


def book_of(path_or_text):
    return BC.book_of(path_or_text)

NOTE_CHAO = '《行事鈔》《義鈔》為比丘律制，部別稱謂須與比丘眾相應'


def _as_tr(rt):
    """三欄報告才切第 3 欄；純譯文（盲翻）原樣回傳。"""
    if rt and ('修正後的譯文' in rt or '分歧與裁決' in rt):
        try:
            return col3(rt)
        except Exception:
            return rt
    return rt


def col3(rt):
    m = re.search(
        r'(?:^|\n)\s*[#*\s]*(?:第\s*)?(?:3|三)\s*(?:欄\s*[｜|：:]|[.、．：:])[^\n]{0,10}(?:修正後|修訂後|定稿|最終)(?:的)?譯文\**\s*[：:\s]*\n?',
        rt)
    if m:
        body = rt[m.end():]
    else:
        i = rt.rfind('修正後的譯文')
        if i < 0:
            _k = rt.rfind('修正')
            _from = _k if _k >= 0 else len(rt)
            mm = re.compile(r'【(?:疏文|記文|鈔文|律文|註文|序文)】').search(rt, _from)
            if mm:
                return re.sub(r'\n{3,}', '\n\n',
                              rt[mm.start():].lstrip('*：: \t\r\n')).strip()
            raise ValueError('回覆檔找不到「修正後的譯文」欄位')
        body = rt[i + len('修正後的譯文'):].lstrip('：: \t')
        if body.startswith('\n'):
            body = body[1:]
    body = body.lstrip('*：: \t\r\n')
    return re.sub(r'\n{3,}', '\n\n', body).strip()


def col3_soft(rt):
    try:
        return col3(rt)
    except Exception:
        return re.sub(r'\n{3,}', '\n\n', rt).strip()


def split_units(body, default_lab='疏文'):
    body = (body or '').strip(' \t\r\n*')
    for _c, _f in (('【疏】', '【疏文】'), ('【記】', '【記文】'), ('【鈔】', '【鈔文】'),
                   ('【律】', '【律文】'), ('【註】', '【註文】'), ('【序】', '【序文】')):
        body = re.sub(r'(?m)^\s*' + _c, _f, body)
    parts = re.split(r'【(疏文|記文|鈔文|律文|註文|序文)】', body)
    out = {}
    if len(parts) >= 3:
        for i in range(1, len(parts) - 1, 2):
            lab, val = parts[i], parts[i + 1].strip()
            if val:
                out[lab] = (out[lab] + '\n\n' + val) if lab in out else val
    if not out and body:
        out[default_lab] = body
    return out


def split_sj(body, has_ji):
    """把譯文切成 (疏／鈔, 記)；無疏標籤時整段歸記文。"""
    body = body.strip(' \t\r\n*')
    if not has_ji:
        return body, ''
    a = re.search(r'【(?:疏文|鈔文|律文|註文|序文)】\s*(.+?)(?=\n\s*\*?\*?【記文】|\Z)', body, re.S)
    b = re.search(r'【記文】\s*(.+?)\Z', body, re.S)
    if b and not a:
        return '', b.group(1).strip()
    if a:
        return a.group(1).strip(), (b.group(1).strip() if b else '')
    return '', body


def _norm(s):
    return re.sub(r'[\s　]', '', norm.normalize(s or ''))


def _same(a, b):
    return _norm(a) == _norm(b)


def _read_side(d, key, out):
    if d is None:
        return None
    p = os.path.join(d, key + '_回.txt')
    return io.open(p, encoding='utf-8').read() if os.path.exists(p) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True)
    ap.add_argument('--a', required=True, help='譯本甲：盲翻回覆目錄')
    ap.add_argument('--b', required=True, help='譯本乙：舊現譯（out）')
    ap.add_argument('--out', required=True)
    ap.add_argument('--force', action='store_true')

    args = ap.parse_args()

    src = os.path.join(B, args.src.replace('/', os.sep))
    out = os.path.join(B, args.out.replace('/', os.sep))
    bdir = None if args.b == 'out' else os.path.join(B, args.b.replace('/', os.sep))
    adir = None if args.a == 'out' else os.path.join(B, args.a.replace('/', os.sep))
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
        if args.b == 'out':
            bp = '__out__'
        else:
            bp = os.path.join(bdir, key + '_回.txt')
            if not os.path.exists(bp):
                continue
        md0 = MI.load(src, fn[:-3]) or {}
        book = md0.get('book') or book_of(os.path.join(src, fn))
        cfg = BC.cfg(book)
        ex = re.search(r'（出處：(.+?)）', t)
        md = MI.load(src, fn[:-3]) or {}
        pre = md.get('pre', '')
        # 甲乙字面完全相同時，無須裁決比較
        _a = _read_side(adir, key, out)
        _b = None if args.b == 'out' else _read_side(bdir, key, out)
        if _a and _b and _same(_a, _b):
            # 仍須產出材料與標準 PASS_A 回覆，否則下游會整組消失
            _md = io.open(os.path.join(src, fn), encoding='utf-8').read().replace('（現譯）', '（譯本甲）')
            _head, _sep, _rest = _md.partition('\n---\n')
            if _sep:
                _jp = (JUDGE_PROMPT.replace('{book_note}', cfg['note'])
                        .replace('{out_format}', BC.fmt_for(book, md.get('units'))))
                _md = _jp + _sep + _rest
            io.open(os.path.join(out, fn), 'w', encoding='utf-8').write(_md)
            _u = os.path.join(out, '回覆', key + '_usage.json')
            os.makedirs(os.path.dirname(_u), exist_ok=True)
            io.open(_u, 'w', encoding='utf-8').write(__import__('json').dumps(
                {'src_hash': __import__('hashlib').md5(_md.encode('utf-8')).hexdigest()[:12],
                 'skip': 'same'}, ensure_ascii=False))
            _j = os.path.join(src, key + '.json')
            if os.path.exists(_j):
                shutil.copy2(_j, os.path.join(out, key + '.json'))
            _w = os.path.join(out, '回覆', key + '_回.txt')
            os.makedirs(os.path.dirname(_w), exist_ok=True)
            try:
                import build_a2 as _A
                _txt = _A.col3(_a)
            except Exception:
                _txt = ''
            io.open(_w, 'w', encoding='utf-8').write(
                '## 1. 結論\n\n`PASS_A`\n\n## 2. 分歧與裁決\n\n兩譯本實質義理無分歧，沿用譯本甲。\n\n'
                '## 3. 修正後的譯文\n\n' + (_txt or _a) + '\n')
            continue
        post = md.get('post', '')

        # 原文各段：優先用 JSON units（含律文／註文／序文），無 JSON 才用正則
        units = md.get('units') or []
        if units:
            parts = [(u.get('lab', ''), u.get('orig', '')) for u in units]
            olds = [(u.get('lab', ''), u.get('tr', '') or '') for u in units]
        else:
            parts = re.findall(r'■ (疏文|記文|鈔文|律文|註文|序文)（原文）\s*\n+(.+?)(?=\n+■ |\n+【後文背景|\Z)', t, re.S)
            olds = re.findall(r'■ (疏文|記文|鈔文|律文|註文|序文)（現譯）\s*\n+(.+?)(?=\n+■ |\n+【後文背景|\Z)', t, re.S)
        has_ji = any(lab == '記文' for lab, _ in parts)
        old_map = {lab: body.strip() for lab, body in olds}
        non_ji_old = next((v for lab, v in old_map.items() if lab != '記文'), '')

        # A／B：以標籤切分（支援律文／註文／序文）
        if adir:
            ap = os.path.join(adir, key + '_回.txt')
            if not os.path.exists(ap):
                print('  [略過] 缺少譯本甲回覆：', key)
                continue
            a_map = split_units(_as_tr(io.open(ap, encoding='utf-8').read()),
                                default_lab=(parts[0][0] if parts else '疏文'))
        else:
            a_map = dict(old_map)
        if args.b == 'out':
            b_map = dict(old_map)
        else:
            b_map = split_units(_as_tr(io.open(bp, encoding='utf-8').read()),
                                default_lab=(parts[0][0] if parts else '疏文'))

        def _pick(m, lab):
            if m.get(lab):
                return m[lab]
            if lab == '記文':
                if m.get('記文'):
                    return m['記文']
                if len(m) == 1:
                    return next(iter(m.values()), '')
                return ''
            return next((v for k, v in m.items() if k != '記文'), '')

        note = cfg['note']
        prompt = JUDGE_PROMPT.replace('{book_note}', note)
        prompt = prompt.replace('{out_format}', BC.fmt_for(book, md.get('units')))

        L = [prompt, '', '---', '', '（出處：%s）' % (ex.group(1) if ex else ''), '']
        if pre:
            L += ['【前文背景（僅供參考）】', '', pre, '']
        L += ['【本次待審單元】', '']
        if md.get('packed'):
            L += ['【分段要求】本單元含多個短段，請保留 [1][2]… 編號逐條對應，勿合併、增減條數或改動編號；正文子序數用一、二、（一）（二），嚴禁額外 [數字] 或 -／*／1. 項目符號。', '']
        for lab, txt in parts:
            lab = lab.strip()
            L += ['■ %s（原文）' % lab, '', txt.strip(), '']
            av = _pick(a_map, lab)
            bv = _pick(b_map, lab)
            L += ['■ %s（譯本甲）' % lab, '', av, '']
            L += ['■ %s（譯本乙）' % lab, '', bv, '']
        if post:
            L += ['【後文背景（僅供參考）】', '', post, '']

        io.open(os.path.join(out, fn), 'w', encoding='utf-8').write('\n'.join(L))
        MI.write_json(out, key, {
            'chunk': (md.get('chunk') or key.rsplit('_', 1)[0]),'key': key,
            's0': md.get('s0'), 's1': md.get('s1'),
            'g0': md.get('g0'), 'g1': md.get('g1'), 'ex': ex.group(1) if ex else '',
                                  'pre': pre, 'post': post,
                                  'book': md.get('book', '') if isinstance(md, dict) else '',
                                  'packed': bool(md.get('packed')) if isinstance(md, dict) else False,
                                  'segments': (md.get('segments') or []) if isinstance(md, dict) else [],
                                  'units': [{'lab': a, 'orig': b} for a, b in parts] })
        n += 1

    print('已產生 %d 份裁決材料 → %s（A 來源：%s）' % (n, args.out, args.a))


if __name__ == '__main__':
    main()
