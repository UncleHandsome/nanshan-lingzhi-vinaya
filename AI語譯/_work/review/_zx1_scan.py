# -*- coding: utf-8 -*-
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _zx1_lib as L

checks = [
    ("01d_上一上", range(2, 64)),
    ("01e_上一上", range(1, 63)),
    ("01f_上一上", range(1, 21)),
]
pats = [u"。、", u"，。", u"。。", u"：：", u"（）", u"〔〕", u"「」", u"  "]
bad = 0
for chunk, rng in checks:
    t, s = L.paras(chunk)
    parts = t.split(s)
    for n in rng:
        p = parts[n - 1]
        a, b = p.count(u"〔"), p.count(u"〕")
        if a != b:
            print(u"BRACKET %s#%d %d/%d" % (chunk, n, a, b)); bad += 1
        for pat in pats:
            if pat in p:
                i = p.find(pat)
                print(u"PAT %s#%d %r ... %s" % (chunk, n, pat, p[max(0,i-15):i+15])); bad += 1
        for ch in (u":", u";", u"("):
            if ch in p:
                i = p.find(ch)
                print(u"ASCII %s#%d %r ... %s" % (chunk, n, ch, p[max(0,i-15):i+15])); bad += 1
print("bad", bad)
