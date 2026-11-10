# -*- coding: utf-8 -*-
import csv, glob, os, re

base = r"AI語譯/_work/review"
pairs = []
for rep in sorted(glob.glob(os.path.join(base, "report_re*.tsv"))):
    tag = re.search(r"report_(re\d+)\.tsv", rep).group(1)
    for fix in glob.glob(os.path.join(base, f"fix_{tag}*.tsv")):
        pairs.append((rep, fix))

for rep, fix in pairs:
    reprows = {}
    with open(rep, encoding="utf-8", newline="") as f:
        r = csv.reader(f, delimiter="\t")
        header = next(r)
        for row in r:
            if len(row) < 10: continue
            d = dict(zip(header, row))
            reprows.setdefault((d["book"], d["chunk"], d["seg"]), d)
    fixrows = {}
    with open(fix, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line: continue
            p = line.split("\t")
            if len(p) != 4: continue
            fixrows[(p[0], p[1], p[2])] = p[3]
    hits = 0
    for k, d in reprows.items():
        if "\n" in d["current"] and k in fixrows:
            hits += 1
            if hits <= 3:
                nparts = len(d["current"].split("\n"))
                nlen = len(fixrows[k])
                # test joining variants
                joined = d["current"].replace("\n", "")
                print(f"[{tag}] {k} parts={nparts} fixlen={nlen} curjoined_len={len(joined)}")
                print("   fix head:", fixrows[k][:100])
                print("   cur head:", d["current"].replace("\n","|")[:100])
    if hits:
        print(f"== {tag}: {hits} newline-rows matched in {os.path.basename(fix)}")
