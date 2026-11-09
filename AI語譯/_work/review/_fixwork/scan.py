# -*- coding: utf-8 -*-
import csv, json, os, re
W = r"AI語譯/_work/review/_fixwork"
OUT = r"AI語譯/_work/review/fix_re3_g1.tsv"
rows = list(csv.reader(open(OUT, encoding="utf-8", newline=""), delimiter="\t", quotechar='"'))
recs = [json.loads(l) for l in open(os.path.join(W, "parsed2.jsonl"), encoding="utf-8")]
cur = {}
for r in recs:
    cur.setdefault((r["chunk"], r["seg"]), r["current"].rstrip("\n"))

pats = {
    "editorial": "（或|或刪|修正為|改為|刪除|補上|應作|應改",
    "doublepunct": "。。|，，|；；|：：|、、|」」|「「",
    "ascii_word": r"[A-Za-z]{2,}",
    "space": " ",
    "emptyquote": "「」",
    "ellipsis": "……",
}
out = []
for r in rows:
    k = (r[1], r[2])
    n = r[3]
    c = cur[k]
    hits = []
    for name, pat in pats.items():
        if re.search(pat, n):
            hits.append(name)
    if hits:
        out.append((k, hits, c, n))
with open(os.path.join(W, "scan.txt"), "w", encoding="utf-8") as f:
    for k, hits, c, n in out:
        f.write(f"### {k} hits={hits}\n")
        for name in hits:
            for m in re.finditer(pats[name], n):
                s = max(0, m.start()-25); e = m.end()+25
                f.write(f"  [{name}] ...{n[s:e]}...\n")
        f.write("\n")
print("rows with hits:", len(out))
