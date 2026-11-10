import csv, difflib

SRC = r"AI語譯/_work/review/report_err.tsv"
OUT = r"AI語譯/_work/review/fix_err_g2.tsv"
REP = r"AI語譯/_work/review/_g2fix/_g2_diff_review.txt"

cur = {}
rows = []
with open(SRC, encoding="utf-8") as f:
    for d in csv.DictReader(f, delimiter="\t"):
        if d["book"] == "03_業疏":
            cur[d["gid"]] = d
            rows.append(d)

fix = []
with open(OUT, encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        if not line:
            continue
        parts = line.split("\t")
        assert len(parts) == 4, (len(parts), line[:60])
        fix.append(parts)

lines = []
lines.append(f"fix rows: {len(fix)}")
# check keys all in report and no dup
keys = [(p[0], p[1], p[2]) for p in fix]
lines.append(f"dup keys: {len(keys) - len(set(keys))}")
rep_keys = {(d['book'], d['chunk'], d['seg']) for d in rows}
lines.append(f"unknown keys: {[k for k in keys if k not in rep_keys]}")

# map seg->gid for review
seg2gid = {(d['chunk'], d['seg']): d['gid'] for d in rows}

for book, chunk, seg, new in fix:
    gid = seg2gid[(chunk, seg)]
    old = cur[gid]["current"]
    sm = difflib.SequenceMatcher(None, old, new)
    chunks = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        ctx_before = old[max(0, i1-30):i1]
        ctx_after = old[i2:i2+30]
        chunks.append(f"  [{tag}] ...{ctx_before}[[OLD:{old[i1:i2]} -> NEW:{new[j1:j2]}]]{ctx_after}...")
    lines.append(f"--- {gid} {chunk} seg{seg}  changed_ops={len(chunks)} oldlen={len(old)} newlen={len(new)}")
    lines.extend(chunks)

with open(REP, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("review written")
