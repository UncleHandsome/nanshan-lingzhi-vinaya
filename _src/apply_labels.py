# -*- coding: utf-8 -*-
"""把四層標籤（【律文】【註文】【疏文】【記文】）套到譯文段首。

結構資料：AI語譯/layers/<book>.json（由 build_layers.py 由 CBETA XML 產生）
用法：
    python _src/apply_labels.py 02_戒疏          # 套用
    python _src/apply_labels.py 02_戒疏 --dry    # 只統計
"""
import os, io, re, json, sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
LAYER_DIR = os.path.join(B, 'AI語譯', 'layers')
SINGLE = {'鈔': '鈔文'}          # 單層書若要標，用這個（預設不標）
LAB = {'律': '律文', '註': '註文', '疏': '疏文', '記': '記文'}
LEAD = re.compile(r'^【(律文|註文|疏文|記文|律|註|疏|記)】')
SKIP_BOOKS = {'03_業疏'}          # 分段未對齊，暫不標


def paras(path):
    return [x for x in re.split(r'\r?\n\r?\n', io.open(path, encoding='utf-8').read()) if x.strip()]


def main():
    book = sys.argv[1]
    dry = '--dry' in sys.argv
    layers = json.load(io.open(os.path.join(LAYER_DIR, book + '.json'), encoding='utf-8'))
    T = os.path.join(B, 'AI語譯', 'out', book)
    stat = {}
    changed = 0
    files = 0
    for key, lay in layers.items():
        p = os.path.join(T, key + '.txt')
        if not os.path.exists(p):
            continue
        ps = paras(p)
        if len(ps) != len(lay):
            print('!! count mismatch', key, len(ps), len(lay))
            continue
        out = []
        for i, seg in enumerate(ps):
            body = seg.strip()
            while True:                      # 去掉重覆的舊標籤（如【疏文】【疏】…）
                nb = LEAD.sub('', body).strip()
                if nb == body:
                    break
                body = nb
            L = lay[i]
            if L in LAB and body:
                new = '【' + LAB[L] + '】' + body
            else:
                new = body
            stat[L if L in LAB else 'title'] = stat.get(L if L in LAB else 'title', 0) + 1
            if new != seg.strip():
                changed += 1
            out.append(new)
        if not dry:
            io.open(p, 'w', encoding='utf-8').write('\n\n'.join(out) + '\n')
        files += 1
    print(book, 'files', files, 'paras', sum(stat.values()), 'changed', changed, stat)


if __name__ == '__main__':
    main()
