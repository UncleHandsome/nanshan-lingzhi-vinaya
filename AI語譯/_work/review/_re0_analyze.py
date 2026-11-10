# -*- coding: utf-8 -*-
"""Analyse each entry: try to extract (old,new) from 建議 and locate old in current paragraph."""
import re, io, json, os
from collections import Counter, defaultdict

OUT = r"AI語譯/_work/review/_re0"
ents = json.load(io.open(os.path.join(OUT, "uniq.json"), encoding="utf-8"))

Q = re.compile(r"「([^「」]*)」")
BQ = re.compile(r"『([^『』]*)』")

def extract_pairs(sug):
    """Return list of (kind, old, new) parsed from suggestion text."""
    out = []
    s = sug.strip()
    # 1) 將「A」改為「B」/ 將「A」修正為「B」 / 把「A」改為「B」
    for m in re.finditer(r"(?:將|把)「([^」]+)」(?:改為|修正為|修改為|改譯為|改作|改成|修正作|更正為)「([^」]+)」", s):
        out.append(("將A改為B", m.group(1), m.group(2)))
    # 2) 「A」改為「B」
    for m in re.finditer(r"「([^」]+)」(?:改為|修正為|修改為|改譯為|改作|改成)「([^」]+)」", s):
        if not any(p[1] == m.group(1) and p[2] == m.group(2) for p in out):
            out.append(("A改為B", m.group(1), m.group(2)))
    if out:
        return out
    # 3) 修正為「B」 / 改為「B」
    m = re.search(r"(?:修正為|修改為|改為|改譯為|更正為)「([^」]+)」", s)
    if m:
        return [("改為X", None, m.group(1))]
    # 4) 刪除「A」/ 刪去
    m = re.search(r"(?:刪除|刪去|刪掉)「([^」]+)」", s)
    if m:
        return [("刪除", m.group(1), "")]
    return [("other", None, None)]

def count_occur(hay, needle):
    if not needle:
        return 0
    return hay.count(needle)

for e in ents:
    e["pairs"] = extract_pairs(e["suggestion"] or "")
    cur = e["current"] or ""
    e["old_in_cur"] = [count_occur(cur, p[1]) if p[1] else None for p in e["pairs"]]
    # quotes from problem / suggestion
    e["q_prob"] = Q.findall(e["problem"] or "")
    e["q_sug"] = Q.findall(e["suggestion"] or "")
    e["prob_in_cur"] = [q for q in e["q_prob"] if q and q in cur]
    e["sugq_in_cur"] = [q for q in e["q_sug"] if q and q in cur]

json.dump(ents, io.open(os.path.join(OUT, "uniq2.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# report
def short(s, n=60):
    s = (s or "").replace("\n", "⏎")
    return s if len(s) <= n else s[:n] + "…"

lines = []
cnt = Counter()
for e in sorted(ents, key=lambda x: (x["book"], x["chunk"], x["seg"], x["gid"])):
    pairs = e["pairs"]
    kind = pairs[0][0]
    cnt[kind] += 1
    cur = e["current"] or ""
    flag = ""
    if kind in ("將A改為B", "A改為B"):
        olds = [p[1] for p in pairs]
        if all(cur.count(o) == 0 for o in olds):
            flag = "OLD-NOT-FOUND"
        elif any(cur.count(o) > 1 for o in olds):
            flag = "OLD-MULTI"
    elif kind == "改為X":
        flag = "NEW-ONLY"
    else:
        flag = "OTHER"
    lines.append("### %s %s %s#%d %s %s [%s]" % (e["gid"], e["book"], e["chunk"], e["seg"], e["prio"], e["type"], flag))
    lines.append("CUR: " + cur)
    lines.append("PROB: " + short(e["problem"], 160))
    lines.append("SUG: " + short(e["suggestion"], 200))
    lines.append("Qprob-in-cur: " + " | ".join(e["prob_in_cur"]))
    lines.append("Qsug-in-cur: " + " | ".join(e["sugq_in_cur"]))
    lines.append("")

io.open(os.path.join(OUT, "report_all.txt"), "w", encoding="utf-8").write("\n".join(lines))
print("kinds:", cnt)
print("flags:", Counter(l.split("[")[-1].rstrip("]") for l in lines if l.startswith("### ")))
