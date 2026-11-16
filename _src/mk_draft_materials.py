# -*- coding: utf-8 -*-
"""單輪草譯材料產生器（接軌 JSON／fmt_for／打包／_hy 混合切法）。

用法：
  python -X utf8 _src/mk_draft_materials.py --src 測試/重譯/資持記/_材料 --out 測試/重譯/資持記/_草譯
  python -X utf8 _src/mk_draft_materials.py --src 測試/重譯/資持記/_材料_hy --out 測試/重譯/資持記/_草譯 --skip-blind 測試/重譯/資持記/_hy_盲翻/回覆
"""
import argparse
import io
import os
import re
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
sys.path.insert(0, os.path.join(B, '_src'))
import book_config as BC   # noqa: E402
import materials_io as MI  # noqa: E402

DRAFT_PROMPT = """你是南山律宗白話譯校編輯，負責將《四分律》與南山著作（{scope}）譯為自然流暢的現代正體書面白話。
下面附有【原文】、前後背景（僅供確認指代與律脈，切勿譯入正文{shuji_ban}），以及文末的【舊譯參考】。

請依序以三欄輸出，**切勿一開始就順著【舊譯參考】的句式修補**：

1. **獨立全譯（甲）**（暫置文末【舊譯參考】，僅依【原文】與前後背景獨立拆解並完整譯出，標籤格式同第 3 欄；僅於確有疑義處並聯檢索，顯明文意勿重複搜查）：
   - **忠實**：不漏條件、實質夾注、音訓與實詞；不增原文所無的細目、背景或考訂。省略之主賓與條件直接融入句中；背景截斷而未見所指時，寧用中性泛稱，不臆補。
   - **律義與文法**：{book_ctx}{shuji_rule}辨古今異義、數理度量（保留原稱）、部別稱謂、科判層級與「文」之所指；嚴核主客施受、持犯開遮與模態強弱、想疑心念、作法時序與界限條件、範圍與否定作用域；句尾虛字須辨結上或領下，引文起迄須分明，勿混同著者評論。
   - **表達**：消除文言直抄與歐化倒裝，輸出語法自足的現代正體書面白話；科判標題保持短語勿擴寫；實詞精準直譯勿籠統委婉。除原文實質夾注與讀音釋義外，不用圓括號添加解說；脫訛補字用 `〔補字〕`，存疑用 `〔疑作X〕`，無實質文義之空符號不強留，勿寫校勘按語。

2. **分歧與裁決**（將第 1 欄「全譯＝甲」與文末「舊譯＝乙」逐句核對）：
   - 依第 1 欄原則比對實質分歧，忽略乙的解說括號與純修辭換詞；**遇甲乙理解有異處，勿因自撰甲譯已順暢而偏袒甲，須回歸原文與檢索覆核，擇善採乙或重修**。每條限寫於同一行內，勿斷行：`[欄別] 原文「……」｜甲作「……」vs 乙作「……」｜裁決（甲優／乙優／重修）：……`（欄別寫 `[疏]`/`[記]` 等單字，勿寫全稱標籤）。
   - 即使甲乙一致，仍須覆核原文有無共同漏譯、施受反轉、錯斷句讀或文言直抄；若須同誤重修，亦依上式列出（「甲乙同作「……」」vs 重修結論）。無任何實質分歧或修正者寫「沿用甲譯」。

3. **修正後的譯文**（以第 1 欄為底本，嚴格貫徹第 2 欄裁決；未列分歧之句照第 1 欄原字照錄，勿趁抄錄暗改字詞；採乙義或重修處須轉寫為第 1 欄之簡明純白話體例，勿直抄乙之解說括號、文言複述或殘留雙譯疊詞。**無論有無分歧皆須於此欄完整輸出正文譯文，不可省略或僅寫代稱**；須照原樣以原標籤開頭，嚴禁自創標籤或夾帶出處網址）：
{out_format}"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--skip-blind', default='', help='已存在盲翻回覆目錄（如 _hy_盲翻/回覆），有有效回覆者跳過')
    ap.add_argument('--force', action='store_true')
    args = ap.parse_args()

    src = os.path.join(B, args.src.replace('/', os.sep))
    out = os.path.join(B, args.out.replace('/', os.sep))
    skip_dir = os.path.join(B, args.skip_blind.replace('/', os.sep)) if args.skip_blind else ''
    os.makedirs(out, exist_ok=True)
    rep = os.path.join(out, '回覆')
    if (os.path.isdir(rep)
            and any(f.endswith('_回.txt') for f in os.listdir(rep))
            and not args.force):
        raise SystemExit('輸出目錄已有回覆，重產材料會造成錯位；若確定覆寫請加 --force：' + out)

    for f in os.listdir(out):
        if f.endswith(('.md', '.json')) and not f.startswith('索引'):
            os.remove(os.path.join(out, f))

    n = skip_old = skip_blind = 0
    for fn in sorted(os.listdir(src)):
        if not fn.endswith('.md'):
            continue
        key = fn[:-3]
        if skip_dir:
            bp = os.path.join(skip_dir, key + '_回.txt')
            if os.path.exists(bp) and os.path.getsize(bp) > 10:
                skip_blind += 1
                continue

        path = os.path.join(src, fn)
        t = io.open(path, encoding='utf-8').read()
        md = MI.load(src, key) or {'ex': '', 'pre': '', 'post': '', 'units': []}
        units = md.get('units') or []
        if not any((u.get('tr') or '').strip() for u in units):
            skip_old += 1
            continue

        book = md.get('book') or BC.book_of(path)
        if book in ('業疏', '疏記') and '（出處：《' in t:
            bm = re.search(r'（出處：《([^》]+)》', t)
            if bm:
                book = bm.group(1)
        cfg = BC.cfg(book)

        labs = list(dict.fromkeys(u.get('lab') for u in units if u.get('lab')))
        scope = cfg['scope']
        bctx = cfg['ctx'][0] if cfg['ctx'][0] else (cfg['note'] + '；' if cfg.get('note') else '')
        sr = cfg['ctx'][1]
        ban = cfg.get('shuji_ban', '')
        if len(labs) == 1:
            scope = labs[0]
            if book in ('業疏', '戒疏'):
                if labs[0] == '記文':
                    sr = '記文釋義與科判動詞須與前文疏義相契，記中「疏云／鈔云」亦須依所釋之書判讀；'
                    ban = '，須與前文疏義相契'
                elif labs[0] == '疏文':
                    sr, ban = '', ''
                else:
                    bctx, sr, ban = '', '', ''
            else:
                sr, ban = '', ''

        prompt = DRAFT_PROMPT.format(
            scope=scope, book_ctx=bctx, shuji_rule=sr, shuji_ban=ban,
            out_format=BC.fmt_for(book, units))

        ex_txt = md.get('ex', '')
        pre_txt = md.get('pre', '')
        post_txt = md.get('post', '')

        L = [prompt, '', '---', '', '（出處：《%s》%s）' % (book or '未知', ex_txt), '']
        if pre_txt:
            L += ['【前文背景（僅供參考，嚴禁譯入正文）】', '', pre_txt, '']
        L += ['【本次待譯單元】', '']
        for u in units:
            L += ['■ %s（原文）' % u['lab'], '', (u.get('orig') or '').strip(), '']
        if md.get('packed'):
            L += ['【分段要求】本單元含多段短文明細，第 1 欄與第 3 欄皆須保留 `[1][2]…` 編號逐條分行對應，'
                  '不可改為 `1. 2.`、合併或增減條數；第 2 欄條目前請加註段號 `[n]`；'
                  '正文子條目序數用一、二、（一）（二），嚴禁額外使用 `[數字]`。', '']
        L += ['【後文背景（僅供參考，嚴禁譯入正文）】', '', post_txt or '（無）', '']
        L += ['【舊譯參考（僅供第 2 欄核對分歧，切勿先依此改寫）】', '']
        for u in units:
            tr = (u.get('tr') or '').strip()
            if tr:
                L += ['■ %s（舊譯）' % u['lab'], '', tr, '']

        io.open(os.path.join(out, fn), 'w', encoding='utf-8').write('\n'.join(L))
        MI.write_json(out, key, {
            'key': key,
            'chunk': md.get('chunk') or key.rsplit('_', 1)[0],
            's0': md.get('s0'), 's1': md.get('s1'),
            'g0': md.get('g0'), 'g1': md.get('g1'),
            'ex': ex_txt, 'pre': pre_txt, 'post': post_txt,
            'book': book, 'packed': bool(md.get('packed')),
            'segments': md.get('segments') or [],
            'units': [{'lab': u['lab'], 'orig': u.get('orig', '')} for u in units],
        })
        n += 1

    print('已產生 %d 份單輪草譯材料（跳過無舊譯 %d、已有盲翻 %d）→ %s'
          % (n, skip_old, skip_blind, args.out))


if __name__ == '__main__':
    main()
