# -*- coding: utf-8 -*-
"""會本_篇14 機械修正第 1–4 步（卷中之二）。

1. 清 鈔87（s114）譯文重複約 1,500 字與資料列殘留。
2. 刪除舊 PDF 分欄標籤：（前半）（後半）（前）（中）（後）。
3. 合併 s157（記488（後）「二中。」）與 s158（記489）。
4. 補 s80/記446、s83/記448、s200/記529 的 〕；修 s200/s201 括號錯亂。

同時回寫上游來源（譯文 txt、資持記細分 txt），避免日後重建復發。
用法：
    python _src/fix_p14_mech.py --dry-run
    python _src/fix_p14_mech.py --apply

注意：本腳本假設「動工前」狀態（s114 譯文 3,370 字、11 個標籤仍在）。
已套用過請先從 `歸檔/會本_篇14_修正前/` 回復，再重新執行。
"""
import io, os, re, sys, json, hashlib
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
HB = os.path.join(B, '白話', '行事鈔資持記句級合編_卷中之二.docx')
YUAN = os.path.join(B, '白話', '會本_篇14_隨戒釋相.docx')
TXT_HB = os.path.join(B, 'AI語譯', 'out', '01_行事鈔', '06a_卷中之二.txt')
TXT_JI1 = os.path.join(B, 'TXT_分卷', '資持記_細分', '08b_中二.txt')
TXT_JI2 = os.path.join(B, 'TXT_分卷', '資持記_細分', '08c_中二.txt')
TXT_TR = os.path.join(B, 'AI語譯', 'out', '資持記', '08c_中二.txt')

LABELS = ['（前半）', '（後半）', '（前）', '（中）', '（後）']
ROW = '\n01_行事鈔\t06a_卷中之二\t21\t'
CHANGES = []


def log(step, target, para, before, after, note=''):
    CHANGES.append(dict(step=step, target=target, para=para,
                        before=len(before), after=len(after), note=note,
                        before_head=before[:40], after_head=after[:40]))


def set_single_run(p, text):
    """整段替換；目標段皆為單一 run。"""
    assert len(p.runs) == 1, '預期單一 run，實際 %d' % len(p.runs)
    p.runs[0].text = text


def drop_trailing(p, ch):
    """移除段末字元；單 run 直接截字，多 run 刪最後一個 run。"""
    assert p.text.endswith(ch), repr(p.text[-20:])
    if len(p.runs) == 1:
        p.runs[0].text = p.text[:-1]
    else:
        r = p.runs[-1]
        assert r.text == ch, repr(r.text)
        r._element.getparent().remove(r._element)


def fix_yuan(apply):
    d = Document(YUAN)
    ps = d.paragraphs
    assert len(ps) == 2856, len(ps)
    assert sum(len(p.text) for p in ps) == 652194

    # 1) 鈔87 譯文：保留資料列之前的一份，刪除資料列＋第二份
    p = ps[1141]
    t = p.text
    assert len(t) == 3370 and ROW in t, (len(t), ROW in t)
    i = t.find(ROW)
    pre, suf = t[:i], t[i + len(ROW):]
    assert pre == suf and len(pre) == 1675
    if apply:
        set_single_run(p, pre)
    log('1', '會本 鈔87（s114）譯文', 1141, t, pre, '刪除重複 1675 字＋資料列 20 字')

    # 4a) 記446 / 記448 補 〕
    for idx, num in ((1064, 446), (1070, 448)):
        p = ps[idx]
        old = p.text
        assert old.startswith('【記%d】' % num) and old.endswith('。')
        new = old + '〕'
        if apply:
            set_single_run(p, new)
        log('4', '會本 記%d' % num, idx, old, new, '補 〕')

    # 4b) 記529 補 〕、記529 譯文補 ）
    p = ps[1302]
    old = p.text
    assert old.startswith('【記529】') and old.endswith('〔有云揀實心非也。')
    new = old + '〕'
    if apply:
        set_single_run(p, new)
    log('4', '會本 記529', 1302, old, new, '補 〕')

    p = ps[1303]
    old = p.text
    assert old.endswith('這種說法是錯誤的。')
    new = old + '）'
    if apply:
        set_single_run(p, new)
    log('4', '會本 記529 譯文', 1303, old, new, '補 ）')

    # 4c) 記530 移除誤植的 ）
    p = ps[1304]
    old = p.text
    assert old.startswith('【記530】') and old.endswith('《十誦》。）')
    new = old[:-1]
    if apply:
        drop_trailing(p, '）')
        assert p.text == new
    log('4', '會本 記530', 1304, old, new, '刪除誤植的 ）')

    if apply:
        d.save(YUAN)
    return len(ps)


def fix_hb(apply):
    d = Document(HB)
    ps = d.paragraphs
    assert len(ps) == 755, len(ps)
    assert sum(len(p.text) for p in ps) == 185694

    pair = lambda k: (ps[3 + 2 * (k - 1)], ps[4 + 2 * (k - 1)])

    # 1) s114 譯文
    tag, p = pair(114)
    assert tag.text.startswith('【鈔】')
    t = p.text
    assert len(t) == 3370 and ROW in t
    i = t.find(ROW)
    pre, suf = t[:i], t[i + len(ROW):]
    assert pre == suf and len(pre) == 1675
    if apply:
        set_single_run(p, pre)
    log('1', '合編 s114（鈔87）譯文', 230, t, pre, '刪除重複 1675 字＋資料列 20 字')

    # 4) 先做括號，避免後面段序變動
    for k, num in ((80, 446), (83, 448)):
        tag, tr = pair(k)
        old = tag.text
        assert old.startswith('【記】') and old.endswith('。')
        new = old + '〕'
        if apply:
            set_single_run(tag, new)
        log('4', '合編 s%d（記%d）' % (k, num), 3 + 2 * (k - 1), old, new, '補 〕')

    tag, tr = pair(200)
    old = tag.text
    assert old.startswith('【記】') and old.endswith('〔有云揀實心非也。')
    new = old + '〕'
    if apply:
        set_single_run(tag, new)
    log('4', '合編 s200（記529）', 401, old, new, '補 〕')

    old = tr.text
    assert old.endswith('這種說法是錯誤的。')
    new = old + '）'
    if apply:
        set_single_run(tr, new)
    log('4', '合編 s200（記529）譯文', 402, old, new, '補 ）')

    tag, tr = pair(201)
    old = tag.text
    assert old.startswith('【記】') and old.endswith('《十誦》。）')
    new = old[:-1]
    if apply:
        drop_trailing(tag, '）')
        assert tag.text == new
    log('4', '合編 s201（記530）', 403, old, new, '刪除誤植的 ）')

    # 2) 刪除 11 個分欄標籤
    label_paras = []
    for k in range(1, 377):
        tag, tr = pair(k)
        for lab in LABELS:
            if lab in tag.text:
                label_paras.append((k, tag, lab))
                break
    assert len(label_paras) == 11, len(label_paras)
    for k, tag, lab in label_paras:
        old = tag.text
        assert old.startswith('【記】' + lab)
        new = old.replace(lab, '', 1)
        if apply:
            set_single_run(tag, new)
        log('2', '合編 s%d' % k, 3 + 2 * (k - 1), old, new, '刪除標籤 ' + lab)

    # 3) 合併 s157 與 s158
    tag157, tr157 = pair(157)
    tag158, tr158 = pair(158)
    if apply:
        assert tag157.text == '【記】二中。', repr(tag157.text)
        assert tr157.text == '第二項中。', repr(tr157.text)
        assert tag158.text.startswith('【記】本明受持'), tag158.text[:20]
        assert tr158.text.startswith('本應說明如何受持'), tr158.text[:20]
        new_tag = '【記】二中。' + tag158.text[3:]
        new_tr = tr157.text + tr158.text
        set_single_run(tag158, new_tag)
        set_single_run(tr158, new_tr)
        for p in (tag157, tr157):
            p._element.getparent().remove(p._element)
        log('3', '合編 s157+s158', 315, tag157.text + ' / ' + tr157.text,
            new_tag[:20] + ' / ' + new_tr[:20], '二中。併入記489，刪除孤立段')
    else:
        log('3', '合編 s157+s158', 315, tag157.text + ' / ' + tr157.text,
            '（二中。＋本明受持…）', '二中。併入記489，刪除孤立段')

    if apply:
        d.save(HB)
    return len(ps)


def fix_txts(apply):
    # 1) 行事鈔譯文：移除資料列與重複
    s = io.open(TXT_HB, encoding='utf-8', newline='').read()
    NL = '\r\n' if '\r\n' in s else '\n'
    paras = [x.strip() for x in re.split(r'\r?\n\r?\n', s) if x.strip()]
    assert len(paras) == 21
    t = paras[20]
    row_nl = NL + ROW[1:]
    assert len(t) == 3370 + (len(NL) - 1) and row_nl in t
    i = t.find(row_nl)
    pre, suf = t[:i], t[i + len(row_nl):]
    assert pre == suf and len(pre) == 1675
    assert s.count(t) == 1
    if apply:
        io.open(TXT_HB, 'w', encoding='utf-8', newline='').write(s.replace(t, pre, 1))
    log('1', 'AI語譯 06a_卷中之二 #21', 20, t, pre, '同步移除重複與資料列')

    # 4) 資持記細分：補記446/448/529 的 〕
    s = io.open(TXT_JI1, encoding='utf-8', newline='').read()
    NL = '\r\n' if '\r\n' in s else '\n'
    pairs = [
        ('非前無根，因此而制也。' + NL + '辨異中',
         '非前無根，因此而制也。〕' + NL + '辨異中', '記446'),
        ('舉過設諫，因制。' + NL + '戒名中',
         '舉過設諫，因制。〕' + NL + '戒名中', '記448'),
    ]
    for old, new, num in pairs:
        assert s.count(old) == 1, (num, s.count(old))
        if apply:
            s = s.replace(old, new, 1)
        log('4', 'TXT 資持記_細分 08b %s' % num, -1, old, new, '補 〕')
    if apply:
        io.open(TXT_JI1, 'w', encoding='utf-8', newline='').write(s)

    s = io.open(TXT_JI2, encoding='utf-8', newline='').read()
    NL = '\r\n' if '\r\n' in s else '\n'
    old = '〔有云揀實心非也。' + NL + '乞無犯者'
    new = '〔有云揀實心非也。〕' + NL + '乞無犯者'
    assert s.count(old) == 1
    if apply:
        s = s.replace(old, new, 1)
        io.open(TXT_JI2, 'w', encoding='utf-8', newline='').write(s)
    log('4', 'TXT 資持記_細分 08c 記529', -1, old, new, '補 〕')

    # 4) 資持記譯文：把落單的 ） 移回上一段
    s = io.open(TXT_TR, encoding='utf-8', newline='').read()
    NL = '\r\n' if '\r\n' in s else '\n'
    old = '這種說法是錯誤的。' + NL + NL + '）乞求而判'
    new = '這種說法是錯誤的。）' + NL + NL + '乞求而判'
    assert s.count(old) == 1
    if apply:
        io.open(TXT_TR, 'w', encoding='utf-8', newline='').write(s.replace(old, new, 1))
    log('4', 'AI語譯 資持記 08c 記529 譯文', -1, old, new, '把 ） 移回前段')


def main():
    apply = '--apply' in sys.argv
    if not apply and '--dry-run' not in sys.argv:
        raise SystemExit('請加 --dry-run 或 --apply')
    print('模式：%s' % ('套用' if apply else 'dry-run'))
    fix_yuan(apply)
    fix_hb(apply)
    fix_txts(apply)
    for c in CHANGES:
        print('[%s] %-32s p%-4s %4d→%-4d %s' % (
            c['step'], c['target'], c['para'], c['before'], c['after'], c['note']))
    if apply:
        print('已套用 %d 項' % len(CHANGES))
        json.dump(CHANGES, io.open(os.path.join(B, '歸檔', '會本_篇14_修正前', 'changes.json'),
                                   'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    else:
        print('dry-run，共 %d 項' % len(CHANGES))


if __name__ == '__main__':
    main()

