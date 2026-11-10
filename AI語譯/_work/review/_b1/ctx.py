# -*- coding: utf-8 -*-
"""從 docs/hebian 或 docs/zhichi 的 HTML 中，取出含關鍵詞的 pair（原文／譯文）。"""
import io, re, html, sys, os, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'


def pairs(path):
    t = io.open(path, encoding='utf-8').read()
    out = []
    for m in re.finditer(r'<div class="pair"[^>]*>(.*?)</div></div>', t, re.S):
        seg = m.group(1)
        o = re.search(r'<div class="o">(.*?)</div>', seg, re.S)
        tr = re.search(r'<div class="t">(.*?)</div>', seg, re.S)
        out.append((html.unescape(re.sub(r'<[^>]+>', '', o.group(1))) if o else '',
                    html.unescape(re.sub(r'<[^>]+>', '', tr.group(1))) if tr else ''))
    return out


def main():
    kw = sys.argv[1]
    files = sys.argv[2:] or [p for p in glob.glob(os.path.join(B, 'docs', 'hebian', '*.html'))]
    for f in files:
        ps = pairs(f)
        for i, (o, tr) in enumerate(ps):
            if kw in o or kw in tr:
                print('=' * 70)
                print('[%s #%d]' % (os.path.basename(f), i))
                print('原文：', o)
                print('譯文：', tr)


if __name__ == '__main__':
    main()
