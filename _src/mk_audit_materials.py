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

AUDIT_PROMPT = '你是南山律典終審校勘員，對照原文找出【待審譯文】的實質錯誤。\n\n請逐句從【原文】獨立拆解文法與律義，再反向驗收【待審譯文】，切勿順著譯文流暢度讀過去；裁決未列分歧之處仍須核對，防範雙譯同誤；即使已發現一處硬傷，仍須核完其餘各句。若有【裁決分歧參考】，逐項驗明所採是否與原文相容，但不得因此忽略未列分歧處。一眼可見之漏譯或贅注直接判定，勿為求安心重複搜尋。{dual_note}{long_note}\n\n### 檢核（只抓實質錯誤，不挑純修辭潤飾）\n1. **律義與部別**（{book_note}）：違背律宗常制、錯混部別、混淆本宗定論與他部異說、科判層級或「文」之所指有誤、引文與著者評論混同、【疏】【記】義理不能互核。\n2. **文法與邏輯**：主客施受反轉、持犯開遮與模態強弱錯置、想疑心念與行為要件失真、時序與界限條件模糊、範圍與否定作用域偏差、句尾虛字斷句致因果轉折反轉、引文起迄錯亂。\n3. **忠實與增刪**：漏譯條件、實質夾注、音訓或實詞；無據增補細目、背景或考訂；誤將背景或他欄專論混入正文；依文脈腦補譯文所無之詞。原文實質夾注、讀音與確須存疑之 `〔補字〕`／`〔疑作X〕` 得保留，空白占位括號不強留。\n4. **表達與殘留**：古今與同形異義誤讀、文言直抄、歐化倒裝、動詞缺主賓、同義重複疊詞、違規添加解說性圓括號、同一核心術語前後譯法歧出，以及網址／按語／自創標籤殘留。\n\n凡涉上述四項實質問題或致語意歧義者，一律列為硬傷判 `FIX`。\n\n### 輸出（勿改寫整段，勿在建議中代寫完整替換句）\n1. **【逐句簡核】**：逐句對照【原文】與【待審譯文】實際字面，核明核心實詞、動詞、主客與界限之實際譯法（禁止按段概括或僅複述原文大意帶過），註明查證結果。\n2. **【結論】**：`PASS` 或 `FIX`（判 FIX 須列至少 1 項硬傷；判 PASS 則下欄只寫「無」）。\n3. **【必改硬傷】**（無硬傷時**只寫「無」一字**，勿寫「經核對…」等說明）：\n   - `[疏/記/鈔/律/註/序，打包段附[n]] 原文「……」→ 待審譯文「……」｜問題：……｜依據：……（引原文或查證書名，摘錄關鍵原句 1–2 句）｜修正方向：……（只寫須補齊或糾正之要素；所涉專詞須兼顧現代白話清晰而不生古今歧義）`'

NOTE_NICAO = ('《比丘尼鈔》須依比丘尼律制與對舉「僧／尼」語境審斷；''檢索《行事鈔》等平行文對讀時，須尊重《尼鈔》對尼眾之改制與節略，不得以比丘制硬套覆蓋')
NOTE_SHUJI = ('《業疏》「文／注」指《隨機羯磨》，《戒疏》「文／注」指《含注戒本》，「律」方指《四分律》，'
              '且【疏】【記】須義理相契，【疏文】勿無故偷搬【記文】專論')


def book_of(path_or_text):
    return BC.book_of(path_or_text)

NOTE_CHAO = '《行事鈔》《義鈔》為比丘律制，部別稱謂須與比丘眾相應'


def _strip_head_paren(s):
    s = (s or '').lstrip('*：: \t\r\n')
    if s[:1] in ('（', '('):
        m = re.match(r'[（(][^）)]*[）)]\s*[：:*]*\s*\n?', s)
        if m and re.search(r'註|注|按|說明|沿用|未改|以下|全文|白話|修訂|完整', m.group(0)):
            s = s[m.end():]
    return s.lstrip('*：: \t\r\n')


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
    if MI.is_keep_a(body):
        return _MARK
    _looks_report = re.search(r'結論|分歧與裁決', body[:80])
    if _looks_report and not _has_lab:
        return None
    if len(re.sub(r'【(?:疏文|記文|鈔文|律文|註文|序文)】', '', body).strip()) < 1:
        return None
    return _strip_head_paren(body)


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
        book = md0.get('book') or book_of(os.path.join(src, fn))
        if book in ('業疏', '疏記') and '（出處：《' in t:
            _bm = re.search(r'（出處：《([^》]+)》', t)
            if _bm:
                book = _bm.group(1)
        if book in ('', '疏記'):
            _bm = re.search(r'（出處：《([^》]+)》', t)
            if _bm:
                book = _bm.group(1)
        cfg = BC.cfg(book)
        note = cfg['note']
        _dual = ('同段【疏】【記】須互核：以【疏文】前提檢核【記文】科判動詞，'
                 '並確認【疏文】未隱沒【記文】所牒實詞。' if book in ('業疏', '戒疏') else '')
        _long = ('本單元為長文切片：若與（本段前文）／（本段後文）語氣連貫，'
                 '勿強補重複主語或結尾句號。' if ('（本段前文）' in t or '（本段後文）' in t or '_長段' in src) else '')
        prompt = (AUDIT_PROMPT.replace('{book_note}', note)
                  .replace('{dual_note}', _dual).replace('{long_note}', _long))

        md = MI.load(src, key) or {}
        srcs = [(u['lab'], u['orig']) for u in md.get('units', [])]
        pre = md.get('pre', '')
        post = md.get('post', '')
        ex = re.search(r'（出處：(.+?)）', t)

        L = [prompt, '', '---', '', '（出處：%s）' % ((ex.group(1) if ex else '') or ('《%s》' % (book or '未知'))), '']
        if pre:
            L += ['【前文背景（僅供參考）】', '', pre, '']
        L += ['【原文】', '']
        for lab, s in srcs:
            L += ['■ %s（原文）' % lab, '', s.strip(), '']
        body = col3_safe(rt)
        if body is None and re.search(r'PASS_A', rt):
            body = _from_jia(t)
        if body == _MARK:
            body = _from_jia(t)
        if body is None:
            print('  ⚠ 略過異常檔：', key)
            continue
        div = divergence(rt)
        if div:
            _brief = []
            for _ln in div.split('\n'):
                _s = _ln.strip()
                if not _s:
                    continue
                _m = re.match(r'(.*?｜裁決[^：:]{0,15}[：:])(.*)', _s)
                if _m:
                    _head = _m.group(1)
                    _why = _m.group(2)
                    _tag = '甲' if '甲優' in (_head + _why) else ('乙' if '乙優' in (_head + _why) else '重修')
                    _srcs = re.findall(r'《[^》]{2,20}》[^，。；\n]{0,8}', _why)
                    _hint = ('（線索：' + '、'.join(_srcs[:2]) + '）') if _srcs else ''
                    _brief.append(_head + '採' + _tag + _hint)
                elif re.match(r'(?:[-*•]|\d+\.)?\s*\[', _s):
                    _mn = re.match(r'\s*(\[\d+\])?', _s)
                    _tag = '甲' if '甲優' in _s else ('乙' if '乙優' in _s else '重修')
                    _brief.append((_mn.group(1) + ' ' if _mn and _mn.group(1) else '')
                                  + '採' + _tag + '（理由格式異常，略）')
            if _brief:
                L += ['【裁決分歧參考（僅供參考，勿照抄）】', '', '\n'.join(_brief), '']
        L += ['【待審譯文】', '', body, '']
        if md.get('packed'):
            L += ['【分段要求】本單元含多個短段，請保留 [1][2]… 編號逐條對應，'
                  '勿合併、增減條數或改動編號。', '']
        if post:
            L += ['【後文背景（僅供參考）】', '', post, '']

        io.open(os.path.join(out, fn), 'w', encoding='utf-8').write('\n'.join(L))
        n += 1

    print('已產生 %d 份二審材料 → %s' % (n, args.out))


if __name__ == '__main__':
    main()
