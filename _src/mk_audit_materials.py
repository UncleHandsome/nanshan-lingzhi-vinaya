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

AUDIT_PROMPT = (
    '你是南山律典終審校勘員，對照原文找出【待審譯文】的實質錯誤。\n\n'
    '請依【原文】逐句拆解文法與律義，再反向驗收【待審譯文】（切勿順著流暢度讀過）；'
    '無論是否附【裁決分歧參考】或已發現硬傷，皆須核畢全文。若有【裁決分歧參考】，須驗明所採是否與原文相容，'
    '不得因此忽略未列分歧處。顯明文意或一眼可見之漏譯贅注可直接判定；但遇疏中略牒（如「某字下」「此下」）、'
    '譯文對原文泛稱補指具體書名／人名、或確有古今撞義而影響義理者，仍須檢索確認，不得以字面通順放行。\n\n'
    '### 檢核（只抓實質錯誤，不挑純修辭與純格式）\n'
    '1. **實質錯誤（見即判 FIX）**：漏譯／無據增補、背景或他欄專論混入正文、動詞缺主賓（僅純分科標目短語除外；凡含散說闡釋之句仍須主賓明確）、'
    '條件句缺結果、術語歧出、生澀文言實詞未譯透或關鍵量詞缺失（致單讀歧義、不知所指，或誤讀為他宗／現代詞義）、'
    '直接引號「……」內半文半白、錯標原典出處／篡改原典文意（引原文＋白話者，白話須在引號外）、'
    '依他典原字改壞本段刻意節改引文；以及網址／按語／自創或錯置標籤殘留'
    '（註：先引原文一句再白話解釋，不視為雙譯疊詞；僅同一句白話重複兩次才判 FIX）。\n'
    '2. **遮蔽原文反讀**：假設不見原文單讀【待審譯文】（僅純分科標目短語除外），須能唯一讀出正確施受、對象、時序與邏輯'
    '（背景截斷或母本無據者，用語法完整之中性泛稱即算通過，不得強求猜補具體對象或條件）；'
    '凡須腦補古文脈絡才能讀通者，判 FIX。\n'
    '3. **不判 FIX**：純修辭換詞；簡繁／異體字、戒名引號、典籍簡稱展開或簡寫、及引文是否保留引號等純表面格式；'
    '依體例保留之被訓釋原詞、專名、儀軌稱謂「某甲」、度量、篇題、「某某反」與未定校勘〔…〕；本段刻意節改所引經律而依本段原文直譯者；'
    '合乎原文脈絡與律制分際的顯義、先引原文再白話解釋，以及不扭曲原義、亦非無據臆造之簡短消歧括注。\n\n'
    '（本段所屬：{book_note}）\n\n'
    '### 檢核通則\n{logic_checklist}\n{dual_note}{long_note}\n'
    '### 輸出（勿改寫整段，勿代寫完整替換句）\n'
    '（段別標籤白名單：【疏文】【記文】【鈔文】【律文】【註文】【序文】；不得自創或混用。）\n\n'
    '【逐句簡核】須分兩步完成（PASS 亦不得略過為一兩行總述）：第一步先遮蔽原文單讀【待審譯文】，'
    '凡指代撞牆、主語斷裂、漏量詞、生澀文言實詞未譯透、前後自相矛盾或事理反常處，先逐點標出；'
    '第二步再逐句對照【原文】核對主客施受、關鍵動詞、條件／否定界限與專詞實義'
    '（顯明無誤之句可按意群簡記相符，長段無須逐字重抄，惟關鍵句與疑點須逐句走到），末句須明言「反讀通順無歧義」或指出斷裂處。\n\n'
    '【結論】\n'
    'PASS 或 FIX（FIX 須列至少 1 項硬傷；PASS 則下欄只寫「無」）。\n\n'
    '【必改硬傷】\n'
    '- 有硬傷每條一行：[打包段附[n]][疏/記/鈔/律/註/序] 原文「……」→ 待審譯文「……」｜問題：……｜'
    '依據：……（引原文或書名卷次，外部查證須摘錄關鍵原句 1–2 句）｜修正方向：……\n'
    '- 凡要求補出具體對象或條件者，依據欄須引出原文或檢索原句；無據不得強令猜補；外部查證須確認確屬本段同一事類脈絡，勿以跨書、跨篇或同篇異節之異釋硬套（須核對論題主體一致）。\n'
    '- 同一專詞或略牒詞於本段多處重現而義理相牽者，或修正將牽動同句領起語／關聯詞者，須一併列出，勿只改一處致前後矛盾。\n'
    '- 無硬傷只寫「無」一字。'
)

def book_of(path_or_text):
    return BC.book_of(path_or_text)


def render_audit(note='', dual='', long='', logic=None):
    """填滿 AUDIT_PROMPT 全部佔位符；未給 logic 時用共用通則，避免佔位符漏填上線。"""
    return (AUDIT_PROMPT.replace('{book_note}', note)
            .replace('{logic_checklist}', BC.LOGIC_CHECKLIST if logic is None else logic)
            .replace('{dual_note}', dual).replace('{long_note}', long))

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
        _labs = {u.get('lab') for u in (md0.get('units') or []) if u.get('lab')}
        _has_dual = (book in ('業疏', '戒疏')) and ('疏文' in _labs and '記文' in _labs)
        _dual = ('\n\n同段【疏】【記】須雙向互核：【疏文】與【記文】之科判、釋義、列舉項數與施受主語須前後相契，'
                 '並確認【疏文】未隱沒【記文】所牒實詞；【疏文】為消歧、還原指代或補全必要量詞之極簡實指不判 FIX，'
                 '僅將【記文】整句專論或無據情節硬搬入【疏文】者始判 FIX。' if _has_dual else '')
        _long = ('\n\n本單元為長文切片：若與（本段前文）／（本段後文）語氣連貫，'
                 '勿強補重複主語或結尾句號（此項優先於「動詞缺主賓」與「遮蔽原文反讀」要求）；'
                 '並請檢查切片接縫：句末多餘句號、重複主語、語氣斷裂。'
                 if (md0.get('long') or '（本段前文）' in t or '（本段後文）' in t) else '')
        note = BC.note_for(book, _labs)
        prompt = render_audit(note, _dual, _long)

        md = MI.load(src, key) or {}
        md = MI.fill_mother(md, md.get('book') or book, t)
        srcs = [(u['lab'], u['orig']) for u in md.get('units', [])]
        pre = md.get('pre', '')
        post = md.get('post', '')
        ex = re.search(r'（出處：(.+?)）', t)

        L = [prompt, '', '---', '', '（出處：%s）' % ((ex.group(1) if ex else '') or ('《%s》' % (book or '未知'))), '']
        if pre:
            L += ['【前文背景（僅供參考，嚴禁譯入正文）】', '', pre, '']
        L += ['【原文】', '']
        if book == '資持記':
            srcs = [('記文' if lab == '鈔文' else lab, s) for lab, s in srcs]
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
        if book == '資持記':
            body = re.sub(r'(?m)^【鈔文】', '【記文】', body)
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
