# -*- coding: utf-8 -*-
"""路線③ 步驟1：盲翻材料（只給原文與背景，不給現譯）。

用法：
  python -X utf8 _src/mk_blind_materials.py --src 測試/回歸11組 --out 測試/回歸11組_盲翻
"""
import argparse
import io
import os

import materials_io as MI

import book_config as BC
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'

BLIND_PROMPT = '你是南山律宗白話譯者，負責將《四分律》與南山著作（{scope}）譯為自然流暢的現代正體書面白話。\n\n只翻譯【本次待譯單元】；前後背景僅供確認指代與律脈，切勿譯入正文{shuji_ban}。\n\n### 原則\n1. **忠實**：不漏條件、實質夾注、音訓與實詞；不增原文所無的細目、背景或考訂。省略之主賓與條件直接融入句中；背景截斷而未見所指時，寧用中性泛稱，不臆補。\n2. **律義與文法**：{book_ctx}{shuji_rule}辨古今與同形異義、數理度量（保留原稱）、部別稱謂、科判層級與「文」之所指；嚴核主客施受、持犯開遮與模態強弱、想疑心念、作法時序與界限條件、範圍與否定作用域；句尾虛字須辨結上或領下，引文起迄須分明，勿混同著者評論。{tail_rule}\n3. **表達**：消除文言直抄與歐化倒裝，輸出語法自足、簡明自然的現代正體書面白話；科判標題與條目綱要保持短語，勿擴寫；涉及戒相、身體或行為要件之實詞須精準直譯，勿改為籠統委婉語。除原文實質夾注與讀音釋義外，不用圓括號添加解說；脫訛補字用 `〔補字〕`，存疑用 `〔疑作X〕`，空白占位括號不強留，勿寫校勘按語。\n照下列完整標籤輸出，勿簡寫或自創標籤：\n{out_format}'

def book_of(path_or_text):
    return BC.book_of(path_or_text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--force', action='store_true')
    args = ap.parse_args()

    src = os.path.join(B, args.src.replace('/', os.sep))
    out = os.path.join(B, args.out.replace('/', os.sep))
    if os.path.isdir(os.path.join(out, '回覆')) and os.listdir(os.path.join(out, '回覆')) and not args.force:
        raise SystemExit('輸出目錄已有回覆，請先移走或加 --force')
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.endswith('.md'):
            os.remove(os.path.join(out, f))

    n = 0
    for fn in sorted(os.listdir(src)):
        if not fn.endswith('.md'):
            continue
        path = os.path.join(src, fn)
        t = io.open(path, encoding='utf-8').read()
        md = MI.load(src, fn[:-3]) or {'ex': '', 'pre': '', 'post': '', 'units': []}
        book = md.get('book') or book_of(path)
        if book in ('業疏', '疏記') and '（出處：《' in t:
            _bm = re.search(r'（出處：《([^》]+)》', t)
            if _bm:
                book = _bm.group(1)
        cfg = BC.cfg(book)
        ex_txt = md.get('ex', '')
        pre_txt = md.get('pre', '')
        post_txt = md.get('post', '')
        srcs = [(u['lab'], u['orig']) for u in md.get('units', [])]

        _labs = [u.get('lab') for u in (md.get('units') or []) if u.get('lab')]
        _labs = list(dict.fromkeys(_labs))
        _scope = cfg['scope']
        _ctx = cfg['ctx'][0]
        _sr = cfg['ctx'][1]
        _ban = cfg.get('shuji_ban', '')
        if len(_labs) == 1:
            _scope = _labs[0]
            if _labs[0] == '記文' and book in ('業疏', '戒疏'):
                _ban = '，須與前文疏義相契'
            elif _labs[0] not in ('疏文', '記文', '律文', '註文', '序文') or book not in ('業疏', '戒疏'):
                _ctx, _sr, _ban = '', '', ''
        _bctx = _ctx
        if cfg.get('note') and not _bctx:
            _bctx = cfg['note']
        prompt = BLIND_PROMPT.format(scope=_scope, book_ctx=_bctx,
                                     shuji_rule=_sr,
                                     shuji_ban=_ban,
                                     tail_rule='',
                                     out_format=BC.fmt_for(book, md.get('units')))

        L = [prompt, '', '---', '', '（出處：《%s》%s）' % (book or '未知', ex_txt), '']
        if pre_txt:
            L += ['【前文背景（僅供參考，嚴禁譯入正文）】', '', pre_txt, '']
        L += ['【本次待譯單元】', '']
        if md.get('packed'):
            L += ['【分段要求】本單元含多段短文明細，請保留 [1][2]… 編號逐條對應翻譯，'
                  '勿合併、增減條數或改動編號；正文內部子條目序數一律用一、二、（一）（二），嚴禁額外使用 [數字]。', '']
        for lab, s in srcs:
            L += ['■ %s（原文）' % lab, '', s.strip(), '']
        if post_txt:
            L += ['【後文背景（僅供參考，嚴禁譯入正文）】', '', post_txt, '']

        io.open(os.path.join(out, fn), 'w', encoding='utf-8').write('\n'.join(L))
        n += 1

    print('已產生 %d 份盲翻材料 → %s' % (n, args.out))


if __name__ == '__main__':
    main()
