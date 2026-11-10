import csv, re, io

fix = r"AI語譯/_work/review/fix_re10.tsv"
rep = r"AI語譯/_work/review/report_re10.tsv"

raw = open(fix, "rb").read()
print("has BOM:", raw.startswith(b"\xef\xbb\xbf"))
print("has CR:", b"\r" in raw)
print("bytes:", len(raw))

txt = raw.decode("utf-8")
lines = txt.split("\n")
if lines and lines[-1] == "":
    lines.pop()
print("lines:", len(lines))

with open(rep, encoding="utf-8", newline="") as f:
    r = csv.reader(f, delimiter="\t")
    header = next(r)
    rows = [dict(zip(header, x)) for x in r if x]

cur = {}
for x in rows:
    k = (x["book"], x["chunk"], x["seg"])
    cur.setdefault(k, x["current"])

ok = True
for i, ln in enumerate(lines, 1):
    parts = ln.split("\t")
    if len(parts) != 4:
        ok = False
        print("BAD FIELD COUNT", i, len(parts))
        continue
    k = tuple(parts[:3])
    new = parts[3]
    if k not in cur:
        ok = False
        print("UNKNOWN KEY", i, k)
    if not new.strip():
        ok = False
        print("EMPTY NEW", i, k)
    if new == cur.get(k):
        ok = False
        print("UNCHANGED", i, k)
    for bad in ("……", "  "):
        if bad in new:
            print("WARN token", bad, i, k)
print("keys in order:", [tuple(l.split("\t")[:3]) for l in lines])
print("unique keys:", len({tuple(l.split("\t")[:3]) for l in lines}))
print("valid:", ok)
