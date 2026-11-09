import io, sys
sys.stdout.reconfigure(encoding="utf-8")
for p in [r"AI語譯\_work\review\fix_re8_g3.tsv", r"AI語譯\_work\review\fix_re8_g1.tsv"]:
    raw=io.open(p,encoding="utf-8",newline="").read()
    lines=raw.split("\n")
    print("=====",p,"len",len(raw),"nlines",len(lines))
    for l in lines[:3]: print("  ",repr(l[:160]))
    import collections
    print("  fieldcounts", collections.Counter(len(l.split("\t")) for l in lines if l.strip()))
    # any line with embedded newline inside field? can't tell; check tabs
    print("  books", collections.Counter(l.split("\t")[0] for l in lines if l.strip()))
