# -*- coding: utf-8 -*-
import json, os, csv

W = r"AI語譯/_work/review/_fixwork"
OUT = r"AI語譯/_work/review/fix_re3_g1.tsv"
recs = [json.loads(l) for l in open(os.path.join(W, "parsed2.jsonl"), encoding="utf-8")]

# ---------- skip decisions (per report row) ----------
skip = {r["idx"]: "no_suggestion" for r in recs if r["mode"] == "skip_nosugg"}
skip[19] = "already_applied"
for i in (10, 12, 83, 171, 188, 191):
    skip[i] = "already_applied"
for i in (135, 136, 137, 138):
    skip[i] = "multiline_current"
# 18 and 22 fix the same sentence; keep 22 (matches surrounding 科判 style)
skip[18] = "duplicate_same_sentence"

# ---------- cleanup of editorial alternatives in auto B ----------
B_REWRITE = {
    2: "都一直到說戒散席",
    125: "自「上品」以下劃分品位",
    195: "從「以」字以下，點明受持詞中稱「若干」的緣由",
    196: "開頭先指示捨衣法",
}

# ---------- manual edits ----------
MAN = {int(k): v for k, v in json.load(open(os.path.join(W, "man.json"), encoding="utf-8")).items()}

errors = []
groups = {}
order = []
for r in recs:
    k = (r["book"], r["chunk"], r["seg"])
    if k not in groups:
        groups[k] = []
        order.append(k)
    groups[k].append(r)

rows_out = []
for k in order:
    members = groups[k]
    book, chunk, seg = k
    base = members[0]["current"]
    if any(m["current"] != base for m in members):
        errors.append((k, "base_mismatch"))
    new = base
    touched = False
    for m in members:
        i = m["idx"]
        if i in skip:
            continue
        if i in MAN:
            touched = True
            spec = MAN[i]
            if spec[0] == "FULL":
                new = spec[1]
                continue
            for old, rep in spec:
                if old == "END":
                    new = new + rep
                elif old == "START":
                    new = rep + new
                elif old == "LEAD":
                    if not new.startswith(rep):
                        errors.append((i, "lead_missing", rep, ""))
                    new = new[len(rep):]
                else:
                    c = new.count(old)
                    if c != 1:
                        errors.append((i, "count", c, old))
                    new = new.replace(old, rep, 1)
        elif m["mode"] == "auto":
            touched = True
            for p in m["ops"]:
                am = p["am"]
                b = B_REWRITE.get(i, p["b"])
                c = new.count(am)
                if c != 1:
                    errors.append((i, "auto_count", c, am))
                new = new.replace(am, b, 1)
        else:
            errors.append((i, "unhandled", m["mode"], ""))
    if not touched:
        continue
    new = new.rstrip("\n")
    if "\n" in new or "\t" in new:
        errors.append((k, "internal_newline"))
    rows_out.append((book, chunk, seg, new, [m["idx"] for m in members if m["idx"] not in skip]))

print("errors:", errors)
print("rows_out:", len(rows_out), "skipped report rows:", len(skip), "segments total:", len(groups))

bad = [(k, "newline") for k in rows_out if "\n" in k[3] or "\t" in k[3]]
print("bad:", bad)

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    for book, chunk, seg, new, ids in rows_out:
        f.write(f"{book}\t{chunk}\t{seg}\t{new}\n")

json.dump({"skip": skip, "count": len(rows_out),
           "segments": [{"book": b, "chunk": c, "seg": s, "ids": ids} for b, c, s, n, ids in rows_out]},
          open(os.path.join(W, "resultmap.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
