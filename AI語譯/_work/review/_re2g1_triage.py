import json, re, difflib

rows = json.load(open(r"AI語譯\_work\review\_re2g1_rows.json", encoding="utf-8"))
OUT = r"AI語譯\_work\review\_re2g1_triage.txt"

def quotes(s):
    return re.findall(r"「(.*?)」", s, re.S)

def lcs_block(a, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    m = sm.find_longest_match(0, len(a), 0, len(b))
    return m

def diffview(old, cur):
    """Return (status, text) where text shows how old maps onto cur."""
    if old in cur:
        return "EXACT", ""
    m = lcs_block(old, cur)
    if m.size < 6:
        return "NOTFOUND", f"lcs={m.size} [{old[:30]}]"
    # window in cur around the match
    a0 = max(0, m.b - 30)
    a1 = min(len(cur), m.b + m.size + max(0, len(old) - m.a) + 30)
    return "FUZZY", cur[a0:a1]

with open(OUT, "w", encoding="utf-8") as f:
    for i, r in enumerate(rows, 1):
        q = quotes(r["suggestion"] or "")
        line = f"[{i}] {r['gid']} {r['chunk']} seg{r['seg']} {r['level']} {r['cls']} | nq={len(q)}"
        f.write(line + "\n")
        for qi, s in enumerate(q[:4]):
            st, info = diffview(s, r["current"])
            tag = "OLD" if qi == 0 else f"Q{qi}"
            if st == "EXACT":
                f.write(f"   {tag} EXACT: {s[:60]}{'...' if len(s) > 60 else ''}\n")
            elif st == "NOTFOUND":
                f.write(f"   {tag} MISSING: {s[:60]}{'...' if len(s) > 60 else ''}\n")
            else:
                f.write(f"   {tag} FUZZY near: {info}\n")
            if qi == len(q) - 1 and len(q) >= 2:
                f.write(f"   NEW: {q[-1][:80]}{'...' if len(q[-1]) > 80 else ''}\n")
                break
print("wrote", OUT)
