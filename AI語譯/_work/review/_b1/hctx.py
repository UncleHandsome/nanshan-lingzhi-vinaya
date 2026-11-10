# -*- coding: utf-8 -*-
"""從 docs/hebian 的 HTML 取出含關鍵詞的 pair（鈔/記 原文＋譯文）。"""
import io, re, html, sys, os, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
PAIR = re.compile(r'<div class="pair" id="(s\d+)"><div class="(o2?|t2?)">(.*?)</div>'
                  r'(?:<div class="(o2?|t2?)">(.*?)</div>)?</div>', re.S)


def txt(x):
    return html.unescape(re.sub(r'<[^>]+>', '', x or '')).strip()


def blocks(path):
    t = io.open(path, encoding='utf-8').read()
    out = []
    for m in PAIR.finditer(t):
        sid, c1, v1, c2, v2 = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
        out.append((sid, c1, txt(v1), c2 or '', txt(v2)))
    return out


def main():
    kw = sys.argv[1]
    ctx = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    files = sys.argv[3:] or sorted(glob.glob(os.path.join(B, 'docs', 'hebian', '*.html')))
    for f in files:
        bs = blocks(f)
        for i, (sid, c1, v1, c2, v2) in enumerate(bs):
            if kw in v1 or kw in v2:
                print('=' * 70)
                print('[%s %s]' % (os.path.basename(f), sid))
                print('原文：', v1)
                print('譯文：', v2)
                if ctx:
                    for j in range(max(0, i - ctx), min(len(bs), i + ctx + 1)):
                        if j == i:
                            continue
                        s2, d1, w1, d2, w2 = bs[j]
                        print('  --', s2, w1[:400])


if __name__ == '__main__':
    main()
