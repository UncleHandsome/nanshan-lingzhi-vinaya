# -*- coding: utf-8 -*-
import json, re, io, os
rows = json.load(open(r"AI語譯\_work\review\_re4g1\rows.json", encoding="utf-8"))
outdir = r"AI語譯\_work\review\_re4g1"
os.makedirs(outdir, exist_ok=True)
BATCH = 20
nl = 0
blocks = []
for i, r in enumerate(rows):
    s = r["suggestion"]; cur = r["current"]
    m = re.match(r"^將「(.+?)」改為「(.+?)」", s) or re.search(r"將「(.+?)」改為「(.+?)」", s)
    old = m.group(1) if m else None
    lines = []
    tag = ""
    if old:
        if old in cur:
            tag = "OLD_IN_CUR"
            k = cur.find(old)
            a = max(0, k-90); b = min(len(cur), k+len(old)+90)
            ctx = cur[a:k] + "⟦" + old + "⟧" + cur[k+len(old):b]
            lines.append("CTX: " + ("…" if a>0 else "") + ctx + ("…" if b<len(cur) else ""))
        else:
            tag = "OLD_GONE"
            lines.append("CUR: " + cur)
    else:
        tag = "NOSIMPLE"
        lines.append("CUR: " + cur)
    blocks.append((i+1, r, tag, lines))

for b in range(0, len(blocks), BATCH):
    fn = os.path.join(outdir, "batch_%02d.txt" % (b//BATCH+1))
    with io.open(fn, "w", encoding="utf-8") as f:
        for n, r, tag, lines in blocks[b:b+BATCH]:
            f.write("### R%d | gid=%s | chunk=%s | seg=%s | %s | %s | %s\n" % (n, r["gid"], r["chunk"], r["seg"], r["level"], r["cls"], tag))
            f.write("P: " + r["problem"] + "\n")
            f.write("S: " + r["suggestion"] + "\n")
            for L in lines:
                f.write(L + "\n")
            f.write("\n")
    print(fn, os.path.getsize(fn))
