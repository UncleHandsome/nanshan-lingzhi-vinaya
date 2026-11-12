# -*- coding: utf-8 -*-
"""Map each 是錯 entry to (book, chunk, seg); compare current para with material 現行譯文 and 建議."""
import os, re, json, difflib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MAT = os.path.join(ROOT, "存疑材料", "補判")
OUTJ = os.path.join(ROOT, "AI語譯", "out")

def rd(p):
    with open(p, encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")

MAP = {}
for i in range(1, 20):
    p = os.path.join(MAT, "新_補_%02d.md" % i)
    txt = rd(p)
    for b in re.split(r"^###\s+", txt, flags=re.M)[1:]:
        lines = b.split("\n")
        seg = lines[0].strip()
        d = {}
        for ln in lines:
            m = re.match(r"^-\s+\*\*(.+?)\*\*[：:]\s*(.*)$", ln.strip())
            if m:
                d[m.group(1)] = m.group(2).strip()
        if "書/chunk#段" in d:
            MAP[seg] = d
p = os.path.join(MAT, "末_補_01.md")
txt = rd(p)
for b in re.split(r"^###\s+", txt, flags=re.M)[1:]:
    lines = b.split("\n")
    seg = lines[0].strip()
    d = {}
    for ln in lines:
        m = re.match(r"^-\s+\*\*(.+?)\*\*[：:]\s*(.*)$", ln.strip())
        if m:
            d[m.group(1)] = m.group(2).strip()
    if "書/chunk#段" in d:
        MAP[seg] = d

bad = json.load(open(os.path.join(os.path.dirname(__file__), "m1_bad.json"), encoding="utf-8"))

def split_loc(loc):
    book, rest = loc.split("／")
    rest = rest.replace("＃", "#")
    chunk, seg = rest.rsplit("#", 1)
    return book, chunk, int(seg)

def para(book, chunk, seg):
    p = os.path.join(OUTJ, book, chunk + ".txt")
    raw = rd(p)
    lines = raw.split("\n")
    idx = [i for i, l in enumerate(lines) if l.strip()]
    return p, lines, idx[seg - 1]

rows = []
for e in bad:
    book, chunk, seg = split_loc(e["loc"])
    p, lines, li = para(book, chunk, seg)
    cur = lines[li]
    mat = MAP[e["id"]].get("現行譯文", "")
    sug = e["sugg"]
    rows.append(dict(id=e["id"], book=book, chunk=chunk, seg=seg, file=p,
                     cur=cur, mat=mat, sug=sug, judge=e["judge"], src=e["file"],
                     cur_eq_mat=(cur == mat), cur_eq_sug=(cur == sug), mat_len=len(mat),
                     cur_len=len(cur), sug_len=len(sug)))

json.dump(rows, open(os.path.join(os.path.dirname(__file__), "m2_rows.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

def sm(a, b, ctx=40):
    if a == b:
        return "IDENTICAL"
    s = difflib.SequenceMatcher(None, a, b, autojunk=False)
    out = []
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        if tag == "equal":
            continue
        out.append("%s [%s]->[%s]" % (tag, a[i1:i2], b[j1:j2]))
    return "\n      ".join(out)

log = []
n_ok = n_same = 0
for r in rows:
    log.append("=" * 78)
    log.append("%s  %s/%s#%d  src=%s" % (r["id"], r["book"], r["chunk"], r["seg"], r["src"]))
    log.append("  cur==mat: %s   cur==sug: %s   len(cur/mat/sug)=%d/%d/%d" %
               (r["cur_eq_mat"], r["cur_eq_sug"], r["cur_len"], r["mat_len"], r["sug_len"]))
    if not r["cur_eq_mat"]:
        log.append("  !! cur != material 現行譯文 ; diff(cur -> mat):")
        log.append("      " + sm(r["cur"], r["mat"]))
    log.append("  diff(current -> 建議):")
    log.append("      " + sm(r["cur"], r["sug"]))
    if r["cur_eq_sug"]:
        n_same += 1
    if r["mat"] and r["cur_eq_mat"]:
        n_ok += 1

log.append("")
log.append("cur==mat: %d/%d ; cur==sug: %d" % (n_ok, len(rows), n_same))
open(os.path.join(os.path.dirname(__file__), "m2_out.txt"), "w", encoding="utf-8").write("\n".join(log))
print("rows", len(rows), "cur==mat", n_ok, "cur==sug", n_same)
