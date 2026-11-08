import io, json, difflib

rows = json.load(open(r"AI語譯/_work/review/_g1_rows.json", encoding="utf-8"))
by_seg = {}
for r in rows:
    by_seg[(r["book"], r["chunk"], r["seg"])] = r

fix = [l.split("\t") for l in io.open(r"AI語譯/_work/review/fix_dir_g1.tsv", encoding="utf-8").read().split("\n") if l]
out = []
assert len(fix) == 67, len(fix)
keys = set()
for f in fix:
    assert len(f) == 4, f
    k = (f[0], f[1], f[2])
    assert k not in keys, k
    keys.add(k)
    r = by_seg[k]
    cur, new = r["current"], f[3]
    assert "\n" not in new and "\t" not in new
    assert new != cur
    sm = difflib.SequenceMatcher(None, cur, new)
    ops = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        ops.append("[%s] %r -> %r" % (tag, cur[i1:i2], new[j1:j2]))
    out.append("ROW gid=%s %s/%s seg=%s  len %d->%d" % (r["gid"], f[0], f[1], f[2], len(cur), len(new)))
    for o in ops:
        out.append("   " + o)
    out.append("")

out.append("=== unmatched report rows: %s" % sorted(set(by_seg) - keys))
io.open(r"AI語譯/_work/review/_g1_verify.txt", "w", encoding="utf-8").write("\n".join(out))
print("ok", len(fix))
