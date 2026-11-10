import csv, re, io, sys, json

path = r"AI語譯/_work/review/report_re10.tsv"
out_path = r"AI語譯/_work/review/fix_re10.tsv"

with open(path, encoding="utf-8", newline="") as f:
    r = csv.reader(f, delimiter="\t")
    header = next(r)
    rows = [dict(zip(header, row)) for row in r if row]

pat = re.compile(r"「([^「」]*)」")

# For suggestions containing only the new text, locate the old span in current by anchors.
ANCHORS = {
    "689-0007": ("應當在自然界之內", "在界內同住也無妨"),
    "695-0007": ("《四分律》通攝年滿十八及童女二種位階", "《四分律》通攝年滿十八及童女二種位階"),
    "695-0010": ("其次離開比丘僧團單獨作法", "其次離開比丘僧團單獨作法"),
    "695-0012": ("如果年滿以下", "特別點出學戒之法"),
    "695-0013": ("第十三至第十九條", "一一作突吉羅罪懺悔"),
}

def build_pairs(row):
    toks = pat.findall(row["suggestion"])
    if len(toks) >= 2:
        olds, news = toks[0::2], toks[1::2]
        if len(olds) != len(news):
            raise SystemExit(f"unpaired quotes: {row['gid']}")
        pairs = []
        for o, n in zip(olds, news):
            os_ = o.split("……")
            ns_ = n.split("……")
            if len(os_) != len(ns_):
                raise SystemExit(f"ellipsis mismatch: {row['gid']} {len(os_)} vs {len(ns_)}")
            pairs.extend(zip(os_, ns_))
        return pairs
    if len(toks) == 1:
        start, end = ANCHORS[row["gid"]]
        cur = row["current"]
        i = cur.find(start)
        if i < 0:
            return None  # cannot locate
        j = cur.find(end, i)
        if j < 0:
            return None
        old = cur[i:j + len(end)]
        return [(old, toks[0])]
    return None

groups = {}
order = []
applied = 0
skipped = 0
details = []

for row in rows:
    key = (row["book"], row["chunk"], row["seg"])
    if key not in groups:
        groups[key] = {"text": row["current"], "rows": []}
        order.append(key)
    pairs = build_pairs(row)
    ok_any = False
    if pairs is None:
        skipped += 1
        details.append((row["gid"], "NO_SUGGESTION_OR_ANCHOR", []))
        continue
    missing = []
    for old, new in pairs:
        if old and old in groups[key]["text"]:
            cnt = groups[key]["text"].count(old)
            groups[key]["text"] = groups[key]["text"].replace(old, new, 1)
            ok_any = True
            details.append((row["gid"], "APPLIED", (old[:20], new[:20], cnt)))
        else:
            missing.append(old)
    if missing:
        details.append((row["gid"], "MISSING", [m[:30] for m in missing]))
        if not ok_any:
            skipped += 1
    if ok_any:
        applied += 1

out_lines = []
for key in order:
    g = groups[key]
    t = g["text"]
    if t.count("\t") or "\n" in t or "\r" in t:
        raise SystemExit(f"bad chars in {key}")
    out_lines.append((key, t))

with open(out_path, "w", encoding="utf-8", newline="") as f:
    for key, t in out_lines:
        f.write("\t".join([key[0], key[1], key[2], t]) + "\n")

with open(r"AI語譯/_work/review/_log_re10.json", "w", encoding="utf-8") as f:
    json.dump({"applied": applied, "skipped": skipped, "out_rows": len(out_lines),
               "details": details}, f, ensure_ascii=False, indent=1)

print("rows:", len(rows), "applied:", applied, "skipped:", skipped, "out_rows:", len(out_lines))
