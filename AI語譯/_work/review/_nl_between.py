# -*- coding: utf-8 -*-
import csv, glob, os, re

base = r"AI語譯/_work/review"
for rep in sorted(glob.glob(os.path.join(base, "report_re*.tsv"))):
    tag = re.search(r"report_(re\d+)\.tsv", rep).group(1)
    reprows = {}
    with open(rep, encoding="utf-8", newline="") as f:
        r = csv.reader(f, delimiter="\t")
        header = next(r)
        for row in r:
            if len(row) < 10: continue
            d = dict(zip(header, row))
            reprows[(d["book"], d["chunk"], d["seg"])] = d
    for fix in glob.glob(os.path.join(base, f"fix_{tag}*.tsv")):
        fixrows = {}
        with open(fix, encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if not line: continue
                p = line.split("\t")
                if len(p) != 4: continue
                fixrows[(p[0], p[1], p[2])] = p[3]
        for k, d in reprows.items():
            if "\n" not in d["current"] or k not in fixrows: continue
            parts = d["current"].split("\n")
            parts = [p for p in parts if p]
            if len(parts) < 2: continue
            fx = fixrows[k]
            p0, p1 = parts[0], parts[1]
            # locate boundary in cur
            a = p0[-12:]
            b = p1[:12]
            ia = fx.find(a)
            ib = fx.find(b)
            if ia == -1 or ib == -1:
                print(f"{tag} {k}: boundary anchors not both found (ia={ia} ib={ib})")
                continue
            between = fx[ia+12:ib]
            print(f"{tag} {k}: between=[{between!r}]  p0end={a}  p1start={b}")
