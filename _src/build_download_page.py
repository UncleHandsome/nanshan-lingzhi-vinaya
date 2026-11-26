# -*- coding: utf-8 -*-
"""產生「下載」頁：把六書白話對照本（單欄／雙欄、DOCX／PDF）整理成表。

流程：
  1. 掃 白話對照本_標楷_{單欄,雙欄}_{DOCX,PDF}/
  2. 複製到 docs/download/（若檔案已存在且大小相同就跳過）
  3. 產生 docs/download.html

執行：python -X utf8 _src/build_download_page.py
"""
import glob
import io
import json
import os
import re
import shutil
import urllib.parse

import site_assets as SA

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
DOCS = os.path.join(B, 'docs')
DL = os.path.join(DOCS, 'download')
SRC = {
    ('單欄', 'DOCX'): os.path.join(B, '白話對照本_標楷_單欄_DOCX'),
    ('單欄', 'PDF'): os.path.join(B, '白話對照本_標楷_單欄_PDF'),
    ('雙欄', 'DOCX'): os.path.join(B, '白話對照本_標楷_雙欄_DOCX'),
    ('雙欄', 'PDF'): os.path.join(B, '白話對照本_標楷_雙欄_PDF'),
}
BOOK_ORDER = ['行事鈔', '戒本疏', '業疏', '尼鈔', '義鈔', '資持記']
BOOK_LABEL = {
    '行事鈔': '四分律刪繁補闕行事鈔',
    '戒本疏': '四分律含注戒本疏行宗記',
    '業疏': '四分律刪補隨機羯磨疏',
    '尼鈔': '四分律比丘尼鈔',
    '義鈔': '四分律拾毘尼義鈔',
    '資持記': '四分律行事鈔資持記',
}


def book_of(fn):
    for k in ['行事鈔', '戒本疏', '業疏', '尼鈔', '義鈔', '資持記']:
        if k in fn:
            return k
    return '其他'


def vol_of(fn):
    m = re.search(r'_(卷[^_]+)_白話對照本', fn)
    return m.group(1) if m else ''


SLUG2BOOK = {'xingshichao': '行事鈔', 'jieshu': '戒本疏', 'yeshu': '業疏',
             'nicao': '尼鈔', 'yichao': '義鈔', 'zhichi': '資持記'}
SLUG2VOL = {'shang': '卷上', 'zhong': '卷中', 'xia': '卷下', 'shou': '卷首',
            '01': '卷一', '02': '卷二', '03': '卷三', '04': '卷四',
            '05': '卷五', '06': '卷六'}


def split_asset(asset, fallback_name=''):
    """xingshichao-shang-single.pdf → ('行事鈔','卷上')"""
    parts = (asset or '').rsplit('.', 1)[0].split('-')
    bk = SLUG2BOOK.get(parts[0]) if parts else None
    vol = SLUG2VOL.get(parts[1]) if len(parts) > 1 else None
    if not bk or not vol:
        f = fallback_name
        bk = bk or book_of(f)
        vol = vol or vol_of(f)
    return bk, vol



def load_manifest():
    p = os.path.join(DOCS, 'download_manifest.json')
    if os.path.exists(p):
        return json.load(io.open(p, encoding='utf-8'))
    return None


def main():
    man = load_manifest()
    if man:
        build_from_manifest(man)
        return
    print('尚無 download_manifest.json：請先跑 make_release.py 上傳到 Releases，'
          '本頁暫不產生（避免把 148 MB 檔案塞進 repo）。')
    return
    os.makedirs(DL, exist_ok=True)
    rows = {}   # (book, vol) -> {('單欄','DOCX'): filename, ...}
    copied = 0
    for key, d in SRC.items():
        if not os.path.isdir(d):
            continue
        for p in glob.glob(os.path.join(d, '*')):
            fn = os.path.basename(p)
            if not (fn.endswith('.docx') or fn.endswith('.pdf')):
                continue
            dst = os.path.join(DL, fn)
            if not (os.path.exists(dst) and os.path.getsize(dst) == os.path.getsize(p)):
                shutil.copyfile(p, dst)
                copied += 1
            rows.setdefault((book_of(fn), vol_of(fn)), {})[key] = (fn, os.path.getsize(p))

    def volkey(v):
        order = {'卷首': 0}
        m = re.search(r'卷([一二三四五六七八九十])', v)
        return (order.get(v, 1), m.group(1) if m else v)

    groups = {}
    for (bk, vol), m in rows.items():
        groups.setdefault(bk, {})[vol] = m

    L = ['<h1>下載・六書白話對照本</h1>',
         '<p class="byline">標楷體 14pt、緊湊排版。單欄適合手機與平板閱讀，雙欄適合列印與對讀。'
         'DOCX 可再自行編輯；PDF 為排版完成版。</p>',
         '<p class="dl-note">檔案較大（PDF 每卷 2–4 MB），建議按需要下載單卷。</p>']

    for bk in BOOK_ORDER:
        if bk not in groups:
            continue
        L.append('<h2 class="sec" id="%s">%s</h2>' % (bk, BOOK_LABEL.get(bk, bk)))
        L.append('<table class="dl-table"><thead><tr>'
                 '<th>卷</th><th>單欄 DOCX</th><th>單欄 PDF</th><th>雙欄 DOCX</th><th>雙欄 PDF</th>'
                 '</tr></thead><tbody>')
        for vol, m in sorted(groups[bk].items(), key=lambda kv: volkey(kv[0])):
            cells = []
            for key in [('單欄', 'DOCX'), ('單欄', 'PDF'), ('雙欄', 'DOCX'), ('雙欄', 'PDF')]:
                item = m.get(key)
                if item:
                    fn, sz = item
                    cells.append('<a class="dl" href="download/%s" download>%s</a>'
                                 % (urllib.parse.quote(fn), fmt_size(sz)))
                else:
                    cells.append('—')
            L.append('<tr><td class="dl-vol">%s</td>%s</tr>'
                     % (vol or '全書', ''.join('<td>%s</td>' % c for c in cells)))
        L.append('</tbody></table>')

    tot = sum(os.path.getsize(os.path.join(DL, f)) for f in os.listdir(DL)) if os.path.isdir(DL) else 0
    L.append('<p class="dl-note">共 %d 個檔案、%s。全部下載請用右上「全選」或逐卷點選。</p>'
             % (len(os.listdir(DL)) if os.path.isdir(DL) else 0, fmt_size(tot)))

    html = SA.page('下載・六書白話對照本｜南山律典', '\n'.join(L), prefix='',
                   book_label='下載', book_short='下載',
                   description='六書白話對照本 Word 與 PDF 下載（單欄／雙欄）。')
    io.open(os.path.join(DOCS, 'download.html'), 'w', encoding='utf-8', newline='\n').write(html)
    print('複製 %d 檔，共 %s → docs/download/ 及 download.html' % (copied, fmt_size(tot)))


def build_from_manifest(man):
    rows = {}
    for f in man.get('files', []):
        fn = f['name']
        bk, vol = split_asset(f.get('asset', ''), fn)
        rows.setdefault((bk, vol), {})[(f['layout'], f['kind'].upper())] = (fn, f['size'], f['url'])

    def volkey(v):
        order = {'卷首': 0}
        m = re.search(r'卷([一二三四五六七八九十])', v)
        return (order.get(v, 1), m.group(1) if m else v)

    groups = {}
    for (bk, vol), m in rows.items():
        groups.setdefault(bk, {})[vol] = m

    L = ['<h1>下載・六書白話對照本</h1>',
         '<p class="dl-note">標楷體 14pt、緊湊排版。單欄適合手機與平板，雙欄適合列印與對讀；'
         'DOCX 可自行編輯，PDF 為排版完成版。檔案存放於 GitHub Releases，不佔用網站流量。<br>'
         '版本：<b>%s</b>　定稿 commit <code>%s</code>　產生 %s　'
         '<a href="%s" target="_blank" rel="noopener">在 GitHub 檢視此版本</a></p>'
         % (man.get('tag', ''), man.get('commit', ''), man.get('generated', ''),
            man.get('release_url', '#'))]

    # v72：左右兩欄書卡（每欄三本），每卡書名＋卷別列(單欄DOCX/單欄PDF/雙欄DOCX/雙欄PDF)
    order = [bk for bk in BOOK_ORDER if bk in groups]
    half = (len(order) + 1) // 2
    cols = [order[:half], order[half:]]
    L.append('<p class="dl-legend">每列：卷 ｜ 單欄 DOCX ｜ 單欄 PDF ｜ 雙欄 DOCX ｜ 雙欄 PDF</p>')
    L.append('<div class="dl-cols">')
    for col in cols:
        L.append('<div class="dl-col">')
        for bk in col:
            vols = sorted(groups[bk].items(), key=lambda kv: volkey(kv[0]))
            L.append('<section class="dl-book"><h2>%s<span class="dl-meta">共 %d 卷</span></h2>'
                     % (BOOK_LABEL.get(bk, bk), len(vols)))
            L.append('<table class="dl-table"><tbody>')
            for vol, m in vols:
                cells = []
                for key in [('單欄', 'DOCX'), ('單欄', 'PDF'), ('雙欄', 'DOCX'), ('雙欄', 'PDF')]:
                    item = m.get(key)
                    if item:
                        fn, sz, url = item
                        cells.append('<a class="dl" href="%s">%s</a>' % (url, fmt_size(sz)))
                    else:
                        cells.append('—')
                L.append('<tr><td class="dl-vol">%s</td>%s</tr>'
                         % (vol or '全書', ''.join('<td>%s</td>' % c for c in cells)))
            L.append('</tbody></table></section>')
        L.append('</div>')
    L.append('</div>')

    tot = sum(f['size'] for f in man.get('files', []))
    L.append('<p class="dl-note">共 %d 個檔案、%s。下載位置為 GitHub Releases 資產。</p>'
             % (len(man.get('files', [])), fmt_size(tot)))
    html = SA.page('下載・六書白話對照本｜南山律典', '\n'.join(L), prefix='',
                   book_label='下載', book_short='下載', body_class='page-download',
                   description='六書白話對照本 Word 與 PDF 下載（單欄／雙欄）。')
    io.open(os.path.join(DOCS, 'download.html'), 'w', encoding='utf-8', newline='\n').write(html)
    print('由 manifest 產生下載頁：%s，%d 檔' % (man.get('tag'), len(man.get('files', []))))


def fmt_size(n):
    if n >= 1048576:
        return '%.1f MB' % (n / 1048576)
    return '%.0f KB' % (n / 1024)


if __name__ == '__main__':
    main()
