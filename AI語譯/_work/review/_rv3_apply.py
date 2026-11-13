# -*- coding: utf-8 -*-
"""apply 複審 edits for 02_戒疏 卷四下之三 (1264-1293)"""
import io, os, sys

BASE = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(BASE, "AI語譯", "out", "02_戒疏")

EDITS = {
    "21a_卷四下之三.txt": [
        ("除為了堅固安全考量之外", "除為了牢固保存的緣故之外"),          # 1264-0007
        ("或者當時患有疾病", "或者當時患有這類疾病", 2),                 # 1265-0008 / 0013
        ("不可攜手牽挽走在路上", "不可攜手走在路上"),                    # 1266-0014
        ("對方手持寶劍", "對方手持劍"),                                  # 1267-0007
        ("是指破壞僧團法規", "是指破壞僧團的和合"),                      # 1269-0001
    ],
    "21b_卷四下之三.txt": [
        ("因此設立了這個法規", "因此制立此法"),                          # 1276-0001
    ],
}

for fn, edits in EDITS.items():
    p = os.path.join(OUT, fn)
    raw = io.open(p, "r", encoding="utf-8", newline="").read()
    assert "\ufeff" not in raw, fn
    crlf = raw.count("\r\n")
    total = len(raw)
    new = raw
    for e in edits:
        old, rep = e[0], e[1]
        want = e[2] if len(e) > 2 else 1
        n = new.count(old)
        assert n == want, "%s: %r count=%d want=%d" % (fn, old, n, want)
        new = new.replace(old, rep)
    assert new.count("\r\n") == crlf, "line ending changed"
    io.open(p, "w", encoding="utf-8", newline="").write(new)
    print("%s: %d bytes -> %d, crlf=%d" % (fn, total, len(new), crlf))
