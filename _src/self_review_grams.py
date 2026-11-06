# -*- coding: utf-8 -*-
"""自我審查：每個記片開頭是否與所屬鈔有詞彙重疊（牒詞特徵）"""
import io, os, re, glob
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))


def grams(s, n=3):
    return {s[i:i + n] for i in range(len(s) - n + 1)}


for f in sorted(glob.glob(os.path.join(B, '白話', '會本_篇*.docx'))):
    d = Document(f)
    ps = [p.text.strip() for p in d.paragraphs]
    cur = ''
    ok = bad = 0
    samples = []
    for i, t in enumerate(ps):
        m = re.match(r'^【鈔\d+】(.+)$', t)
        if m:
            cur = han(m.group(1)); continue
        m = re.match(r'^【記\d+[^】]*】(.+)$', t)
        if m and cur:
            head = han(m.group(1))[:24]
            if not head:
                continue
            inter = grams(head) & grams(cur)
            if inter:
                ok += 1
            else:
                bad += 1
                if len(samples) < 2:
                    samples.append((t[:26], cur[:18]))
    tot = ok + bad
    print('%-24s 記片%3d 有牒詞%3d (%3.0f%%) 無%3d %s' % (
        os.path.basename(f)[:-5], tot, ok, 100.0 * ok / max(1, tot), bad, samples[:1]))
