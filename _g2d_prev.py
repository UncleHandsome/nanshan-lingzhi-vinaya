import io
for p in [r"AI語譯/_work/review/fix_loc_g2.tsv", r"AI語譯/_work/review/fix_t1pack.tsv", r"AI語譯/_work/review/fix_t2b.tsv"]:
    raw = io.open(p, encoding="utf-8").read()
    lines = raw.split("\n")
    ncols = set(l.count("\t") for l in lines if l)
    print(p, "lines", len([l for l in lines if l]), "colcounts", ncols)
    print("   sample:", lines[0][:120])
