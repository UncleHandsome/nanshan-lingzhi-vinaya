# -*- coding: utf-8 -*-
"""Independent verification: compare backup vs current, re-check every applied paragraph."""
import json, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
BAK = os.path.join(ROOT, "歸檔", "末批套用前")
rows = json.load(open(os.path.join(HERE, "m2_rows.json"), encoding="utf-8"))
POST = {"1525-0001": [("而非從見聞而來", "而非從眼見耳聞而來")]}

def rb(p):
    return open(p, "rb").read()

def paras(b):
    t = b.decode("utf-8-sig")
    ls = t.split("\n")
    return [l for l in ls if l.strip()], ls

groups = collections.OrderedDict()
for r in rows:
    groups.setdefault((r["book"], r["chunk"]), []).append(r)

fail = []
print("%-34s %4s %4s %4s %6s %6s %s" % ("file", "para", "eol", "diff", "appl", "sugok", "status"))
tot_p = tot_appl = tot_diff = 0
for (book, chunk), ents in groups.items():
    cur_path = os.path.join(ROOT, "AI語譯", "out", book, chunk + ".txt")
    bak_path = os.path.join(BAK, book, chunk + "_z.txt")
    cb, bb = rb(cur_path), rb(bak_path)
    cp, cls = paras(cb)
    bp, bls = paras(bb)
    eol_c = collections.Counter(("CRLF" if l.endswith("\r") else "LF") for l in cp)
    eol_b = collections.Counter(("CRLF" if l.endswith("\r") else "LF") for l in bp)
    diff = sum(1 for a, b in zip(bp, cp) if a != b) + abs(len(bp) - len(cp))
    appl = 0
    sugok = 0
    for r in ents:
        want = r["sug"]
        for a, b in POST.get(r["id"], []):
            want = want.replace(a, b)
        got = cp[r["seg"] - 1].rstrip("\r")
        if got == want:
            sugok += 1
        if bp[r["seg"] - 1].rstrip("\r") != got:
            appl += 1
    ok = (len(bp) == len(cp) and eol_b == eol_c and diff == appl == sugok == len(ents))
    if not ok:
        fail.append((book, chunk, len(bp), len(cp), dict(eol_b), dict(eol_c), diff, appl, sugok, len(ents)))
    tot_p += len(cp); tot_appl += appl; tot_diff += diff
    print("%-34s %4d %4s %4d %6d %6d %s" % (book + "/" + chunk, len(cp),
          "CRLF" if eol_c.get("CRLF") else "LF", diff, appl, sugok, "OK" if ok else "FAIL"))
print()
print("files=%d  total paras=%d  applied=%d  diff paras=%d  failures=%d" %
      (len(groups), tot_p, tot_appl, tot_diff, len(fail)))
for f in fail:
    print("FAIL:", f)

# BOM / encoding sanity
for (book, chunk), ents in groups.items():
    p = os.path.join(ROOT, "AI語譯", "out", book, chunk + ".txt")
    b = rb(p)
    assert not b.startswith(b"\xef\xbb\xbf"), p
    b.decode("utf-8")
print("encoding ok (utf-8, no BOM)")
