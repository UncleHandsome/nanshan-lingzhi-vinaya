import json, re, difflib

rows = json.load(open(r"AI語譯\_work\review\_re2g1_rows.json", encoding="utf-8"))
BASE = r"AI語譯\_work\review\_re2g1_rev_"

def quotes(s):
    return re.findall(r"「(.*?)」", s, re.S)

def diffview(old, cur):
    if old in cur:
        return "EXACT", ""
    sm = difflib.SequenceMatcher(None, old, cur, autojunk=False)
    m = sm.find_longest_match(0, len(old), 0, len(cur))
    if m.size < 6:
        return "NOTFOUND", ""
    a0 = max(0, m.b - 40)
    a1 = min(len(cur), m.b + m.size + max(0, len(old) - m.a) + 40)
    return "FUZZY", cur[a0:a1]

BATCH = 34
n = len(rows)
for b, start in enumerate(range(0, n, BATCH), 1):
    end = min(n, start + BATCH)
    with open(f"{BASE}{b:02d}.txt", "w", encoding="utf-8") as f:
        for i in range(start, end):
            r = rows[i]
            q = quotes(r["suggestion"] or "")
            st = "NOQUOTE"
            info = ""
            if q:
                st, info = diffview(q[0], r["current"])
            f.write(f"[{i+1}] {r['gid']} {r['chunk']} seg{r['seg']} {r['level']} {r['cls']} | {st}\n")
            f.write(f"P: {r['problem']}\n")
            f.write(f"S: {r['suggestion']}\n")
            if info:
                f.write(f"W: {info}\n")
    print("wrote batch", b, start + 1, end)
