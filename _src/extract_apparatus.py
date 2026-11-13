# -*- coding: utf-8 -*-
"""抽取 CBETA XML 校勘（app/lem/rdg），以錨點回連正文，建可查索引。

輸出：測試/校勘索引.tsv（書｜行號｜上下文｜正字｜異文｜版本）
"""
import glob
import io
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
XMLDIR = os.path.join(B, '_src', 'xml')
OUT = os.path.join(B, '測試', '校勘索引.tsv')

BOOKS = {
    'T40n1804': '四分律刪繁補闕行事鈔',
    'T40n1805': '四分律行事鈔資持記',
    'X39n0714': '含注戒本疏行宗記(1-3)',
    'X40n0714': '含注戒本疏行宗記(3-4)',
    'X40n0724': '四分比丘尼鈔',
    'X41n0728': '羯磨疏濟緣記',
    'X44n0747': '拾毗尼義鈔',
}


def strip_tags(s):
    s = re.sub(r'<anchor[^>]*/>', '', s)
    s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'\s+', '', s)


def main():
    rows = []
    for p in sorted(glob.glob(os.path.join(XMLDIR, '*.xml'))):
        key = os.path.basename(p)[:-4]
        title = BOOKS.get(key, key)
        t = io.open(p, encoding='utf-8', errors='ignore').read()

        # 建錨點索引：id -> (位置, 最近 lb, 上下文)
        anchors = {}
        for m in re.finditer(r'<anchor xml:id="(beg[^"]+)"', t):
            aid = m.group(1)
            pos = m.start()
            before = t[max(0, pos - 4000):pos]
            lbs = re.findall(r'<lb[^>]*n="([^"]+)"', before)
            lb = lbs[-1] if lbs else ''
            ctx = strip_tags(t[max(0, pos - 120):pos + 120])
            anchors[aid] = (lb, ctx)

        # 解析文末校注
        for m in re.finditer(r'<app([^>]*)>(.*?)</app>', t, re.S):
            attrs, blk = m.group(1), m.group(2)
            frm = re.search(r'from="#([^"]+)"', attrs)
            if not frm:
                continue
            lem = re.search(r'<lem[^>]*>(.*?)</lem>', blk, re.S)
            rdgs = re.findall(r'<rdg[^>]*wit="([^"]*)"[^>]*>(.*?)</rdg>', blk, re.S)
            if not lem or not rdgs:
                continue
            lb, ctx = anchors.get(frm.group(1), ('', ''))
            lem_txt = strip_tags(lem.group(1)) or '（無）'
            for wit, val in rdgs:
                v = strip_tags(val) or '（無）'
                w = wit.replace('#wit.', '')
                rows.append((title, lb, ctx[:50], lem_txt[:30], v[:30], w))

    io.open(OUT, 'w', encoding='utf-8').write(
        '書\t行號\t上下文\t正字\t異文\t版本\n' +
        '\n'.join('\t'.join(r) for r in rows) + '\n')
    print('抽出校勘 %d 條 → %s' % (len(rows), OUT))
    from collections import Counter
    for k, v in Counter(r[0] for r in rows).most_common():
        print('  %-26s %d' % (k, v))


if __name__ == '__main__':
    main()