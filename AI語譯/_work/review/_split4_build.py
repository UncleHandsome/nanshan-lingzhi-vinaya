# -*- coding: utf-8 -*-
"""Build split_4.tsv / split_4_src.tsv for the 4 merged segments."""
from pathlib import Path

B = Path(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
SRC = B / "TXT_分卷" / "資持記_細分"
OUT = B / "AI語譯" / "out" / "資持記"
REV = B / "AI語譯" / "_work" / "review"

def paras(path):
    return [l for l in path.read_text(encoding="utf-8-sig").splitlines() if l.strip()]

src_a = paras(SRC / "04a_上三.txt")
src_c = paras(SRC / "04c_上三.txt")
tr_a = paras(OUT / "04a_上三.txt")
tr_c = paras(OUT / "04c_上三.txt")

# content paragraph N (1-based, header = first 4 non-empty lines) -> index N+3
def sget(lst, seg):
    return lst[seg + 3]

log = []
def split_at(text, cuts, label):
    parts = []
    prev = 0
    for c in cuts:
        parts.append(text[prev:c])
        prev = c
    parts.append(text[prev:])
    assert "".join(parts) == text, label
    assert all(p.strip() for p in parts), (label, [len(p) for p in parts])
    return parts

def split_tr(text, anchors, label):
    parts = []
    rest = text
    for a in anchors:
        i = rest.find(a)
        assert i > 0, (label, a, i)
        parts.append(rest[:i])
        rest = rest[i:]
    parts.append(rest)
    assert "".join(parts) == text, label
    assert all(p.strip() for p in parts)
    return parts

rows_tr = []
rows_src = []

# ---- 1) 04a seg 12 : cut at 101 ----
s = sget(src_a, 12)
assert s[101:].startswith("第二所對，結界中"), s[101:105]
sp = split_at(s, [101], "04a#12")
t = tr_a[11]
anchor = "第二項「所對的境界」"
tp = split_tr(t, [anchor], "04a#12 tr")
log.append(("04a#12 src", [len(x) for x in sp], sp[0][-25:], sp[1][:25]))
log.append(("04a#12 tr", [len(x) for x in tp], tp[0][-25:], tp[1][:25]))
for i in range(2):
    rows_src.append(("04a_上三.txt", 12, i + 1, sp[i]))
    rows_tr.append(("04a_上三.txt", 12, i + 1, tp[i]))

# ---- 2) 04a seg 16 : cuts at 26 and 74 ----
s = sget(src_a, 16)
assert s[26:].startswith("三中分二，初釋緣相"), s[26:30]
assert s[74:].startswith("文下，二引本制"), s[74:78]
sp = split_at(s, [26, 74], "04a#16")
t = tr_a[15]
tp = split_tr(t, ["第三項之中分為兩部分", "從「文」字以下，第二部分引用原本的戒制"], "04a#16 tr")
log.append(("04a#16 src", [len(x) for x in sp], [x[-20:] for x in sp], [x[:20] for x in sp]))
log.append(("04a#16 tr", [len(x) for x in tp], [x[-20:] for x in tp], [x[:20] for x in tp]))
for i in range(3):
    rows_src.append(("04a_上三.txt", 16, i + 1, sp[i]))
    rows_tr.append(("04a_上三.txt", 16, i + 1, tp[i]))

# ---- 3) 04a seg 52 : cut at 109 ----
s = sget(src_a, 52)
assert s[109:].startswith("顯德中，初科，初引示"), s[109:113]
sp = split_at(s, [109], "04a#52")
t = tr_a[51]
tp = split_tr(t, ["在顯揚戒德的文段中"], "04a#52 tr")
log.append(("04a#52 src", [len(x) for x in sp], sp[0][-25:], sp[1][:25]))
log.append(("04a#52 tr", [len(x) for x in tp], tp[0][-25:], tp[1][:25]))
for i in range(2):
    rows_src.append(("04a_上三.txt", 52, i + 1, sp[i]))
    rows_tr.append(("04a_上三.txt", 52, i + 1, tp[i]))

# ---- 4) 04c seg 45 : cut before "9 釋師資篇" (i.e. 85) ----
s = sget(src_c, 45)
i9 = s.find("9 釋師資篇")
assert i9 == 85, i9
assert s[i9 + 2:].startswith("釋師資篇"), s[i9:i9 + 10]
sp = split_at(s, [i9], "04c#45")
t = tr_c[44]
tp = split_tr(t, ["第9篇〈釋師資篇〉"], "04c#45 tr")
log.append(("04c#45 src", [len(x) for x in sp], sp[0][-25:], sp[1][:30]))
log.append(("04c#45 tr", [len(x) for x in tp], tp[0][-25:], tp[1][:30]))
for i in range(2):
    rows_src.append(("04c_上三.txt", 45, i + 1, sp[i]))
    rows_tr.append(("04c_上三.txt", 45, i + 1, tp[i]))

# ---- write ----
def write_tsv(path, rows):
    for r in rows:
        f = r[3]
        assert "\t" not in f and "\n" not in f and "\r" not in f, r[:3]
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write("\t".join([r[0], str(r[1]), str(r[2]), r[3]]) + "\n")

write_tsv(REV / "split_4.tsv", rows_tr)
write_tsv(REV / "split_4_src.tsv", rows_src)

print("rows_tr", len(rows_tr), "rows_src", len(rows_src))
for x in log:
    print(x)
