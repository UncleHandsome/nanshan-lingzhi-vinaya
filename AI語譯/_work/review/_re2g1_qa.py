import io, re

p = r"AI語譯\_work\review\fix_re2_g1.tsv"
lines = io.open(p, encoding="utf-8").read().split("\n")
if lines and lines[-1] == "":
    lines.pop()
print("lines:", len(lines))
bad = []
for n, ln in enumerate(lines, 1):
    f = ln.split("\t")
    if len(f) != 4:
        bad.append((n, "fields", len(f)))
        continue
    book, chunk, seg, t = f
    if book != "資持記":
        bad.append((n, "book", book))
    if not t:
        bad.append((n, "empty"))
        continue
    if t != t.strip():
        bad.append((n, "space"))
    for a, b in [("「", "」"), ("（", "）"), ("〔", "〕"), ("《", "》")]:
        if t.count(a) != t.count(b):
            bad.append((n, f"bracket {a}{b} {t.count(a)}/{t.count(b)}", t[:40]))
    for pat in ["，，", "。。", "；；", "，，", "、、", "：："]:
        if pat in t:
            bad.append((n, "dup punct " + pat, t[max(0, t.find(pat) - 15):t.find(pat) + 15]))
    if re.search(r"[，、；：。]$", t) is None and not re.search(r"[」）〕》]", t[-1]):
        bad.append((n, "odd ending", t[-20:]))
    if re.match(r"^[，、；：。]", t):
        bad.append((n, "odd start", t[:20]))
print("issues:", len(bad))
for b in bad[:40]:
    print(b)
