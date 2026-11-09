# -*- coding: utf-8 -*-
import json, re, io, sys, importlib.util
from collections import defaultdict

rows = json.load(open(r"AI語譯\_work\review\_re4g1\rows.json", encoding="utf-8"))
spec = importlib.util.spec_from_file_location("b", r"AI語譯\_work\review\_re4g1\build.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)

QUOTES = b.QUOTES
def norm(t):
    return re.sub(r"[「」『』\"'“”‘’\s]", "", t)

def find_norm_span(text, old):
    nt, idx = b.norm_map(text)
    no = norm(old)
    k = nt.find(no)
    if k < 0:
        return None
    return idx[k], idx[k+len(no)-1] + 1

def style_new(new, span):
    if "「" in span and "『" not in span:
        new = new.replace("『", "「").replace("』", "」")
    elif "『" in span and "「" not in span:
        new = new.replace("「", "『").replace("」", "』")
    return new

segcur = {}
bad_seg = []
for i, r in enumerate(rows, 1):
    k = (r["chunk"], r["seg"])
    if k in segcur and segcur[k] != r["current"]:
        bad_seg.append((i, k))
    segcur[k] = r["current"]
assert not bad_seg, bad_seg

texts = dict(segcur)
changes = []
errors = []

for i, r in enumerate(rows, 1):
    k = (r["chunk"], r["seg"])
    t = texts[k]
    st = b.status[i]
    if st == "skip":
        continue
    ops = b.ops.get(i)
    fz = b.fuzzy.get(i)
    if ops:
        for old, new in ops:
            if old in t:
                cnt = t.count(old)
                t = t.replace(old, new, cnt)
                changes.append((i, r["seg"], old, new, "exact"))
            elif new in t:
                changes.append((i, r["seg"], old, new, "already"))
            else:
                errors.append((i, "EXACT-NOTFOUND", old[:60]))
    elif fz:
        for old, new in fz:
            sp = find_norm_span(t, old)
            if sp is None:
                if norm(new) in norm(t):
                    changes.append((i, r["seg"], old, new, "already"))
                else:
                    errors.append((i, "FUZZY-NOTFOUND", old[:60]))
                continue
            a, z = sp
            if old[0] in "「『" and a > 0 and t[a-1] in "「『":
                a -= 1
            if old[-1] in "」』" and z < len(t) and t[z] in "」』":
                z += 1
            span = t[a:z]
            nn = style_new(new, span)
            t = t[:a] + nn + t[z:]
            changes.append((i, r["seg"], span, nn, "fuzzy"))
    texts[k] = t

print("errors:", len(errors), errors)
print("changes:", len(changes))
done = [i for i, r in enumerate(rows, 1) if b.status[i] != "skip"]
print("done rows:", len(done), "skipped:", 157 - len(done))

# integrity
for i in done:
    r = rows[i-1]
    t = texts[(r["chunk"], r["seg"])]
    assert "\t" not in t and "\n" not in t and "\r" not in t, i

out = []
seen = set()
for i in done:
    r = rows[i-1]
    key = (r["book"], r["chunk"], r["seg"])
    if key in seen:
        continue
    seen.add(key)
    t = texts[(r["chunk"], r["seg"])]
    out.append("%s\t%s\t%s\t%s" % (r["book"], r["chunk"], r["seg"], t))
io.open(r"AI語譯\_work\review\fix_re4_g1.tsv", "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
print("wrote", len(out), "unique segments")

log = ["R%d seg=%s [%s]\n  - %s\n  + %s" % (i, seg, how, old, new) for i, seg, old, new, how in changes]
io.open(r"AI語譯\_work\review\_re4g1\difflog.txt", "w", encoding="utf-8").write("\n".join(log))
