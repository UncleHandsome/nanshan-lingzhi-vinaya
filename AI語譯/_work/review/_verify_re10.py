import csv, difflib

rep = r"AI語譯/_work/review/report_re10.tsv"
fix = r"AI語譯/_work/review/fix_re10.tsv"

with open(rep, encoding="utf-8", newline="") as f:
    r = csv.reader(f, delimiter="\t")
    header = next(r)
    rows = [dict(zip(header, x)) for x in r if x]

base = {}
order = []
for x in rows:
    k = (x["book"], x["chunk"], x["seg"])
    if k not in base:
        base[k] = x["current"]
        order.append(k)

with open(fix, encoding="utf-8", newline="") as f:
    lines = [ln.rstrip("\n") for ln in f if ln.strip("\n")]

assert len(lines) == len(order), (len(lines), len(order))
for ln, k in zip(lines, order):
    parts = ln.split("\t")
    assert len(parts) == 4, (k, len(parts))
    assert tuple(parts[:3]) == k, (parts[:3], k)
    new = parts[3]
    old = base[k]
    assert "\n" not in new and "\r" not in new
    sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
    print("=" * 30)
    print(k[0], k[1], k[2], "ratio=%.4f" % sm.ratio(), "len %d -> %d" % (len(old), len(new)))
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        print("  [%s] OLD:%r" % (tag, old[i1:i2]))
        print("        NEW:%r" % (new[j1:j2],))
print("total lines:", len(lines))
