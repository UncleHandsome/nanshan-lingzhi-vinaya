# -*- coding: utf-8 -*-
"""整理待補譯段落（戒疏 20b、資持記 12a/12b、義鈔 01b/02b）→ _work/miss_input.json"""
import os, io, re, json, difflib

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
LEAD = re.compile(r'^(【[^】]{1,6}】)+')
norm = lambda s: re.sub(r'[\s\u3000]', '', LEAD.sub('', s.strip()))

TARGETS = [
    ('02_戒疏', '02_戒疏', '20b_卷四下之二'),
    ('資持記', '資持記_細分', '12a_中四下'),
    ('資持記', '資持記_細分', '12b_中四下'),
    ('05_拾毗尼義鈔', '05_拾毗尼義鈔', '01b_卷上之一'),
    ('05_拾毗尼義鈔', '05_拾毗尼義鈔', '02b_卷上之二'),
]
FORCE = {'01b_卷上之一', '02b_卷上之二'}   # 整塊重譯


def main():
    out = []
    for tag, sd, key in TARGETS:
        S = os.path.join(B, 'TXT_分卷', sd, key + '.txt')
        T = os.path.join(B, 'AI語譯', 'out', tag, key + '.txt')
        sp = [x.strip() for x in io.open(S, encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(T, encoding='utf-8').read()) if x.strip()]
        segs = []
        for i in range(min(len(sp), len(tt))):
            a, b = norm(sp[i]), norm(tt[i])
            if key in FORCE or a == b or difflib.SequenceMatcher(None, a, b).ratio() >= 0.95:
                segs.append(dict(seg=i + 1, src=sp[i], cur=tt[i]))
        if segs:
            out.append(dict(book=tag, key=key, total=len(sp), segs=segs))
            print('%-14s %-18s 未譯 %3d / %3d' % (tag, key, len(segs), len(sp)))
    json.dump(out, io.open(os.path.join(B, 'AI語譯', '_work', 'miss_input.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('total segs', sum(len(x['segs']) for x in out))


if __name__ == '__main__':
    main()
