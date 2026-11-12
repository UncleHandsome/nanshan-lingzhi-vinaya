# -*- coding: utf-8 -*-
"""Parse re0.txt + 存疑 source files into structured records; dump matching report."""
import os, re, json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SU = os.path.join(ROOT, "存疑材料")
OUT = os.path.join(SU, "補判", "_tools")

def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

# ---------- 1. re0 ----------
re0 = rd(os.path.join(SU, "re0.txt"))
entries = []
cur = None
for ln in re0.split("\n"):
    m = re.match(r"^### (.+?)｜(是錯|不是錯|材料不足)\s*$", ln)
    if m:
        if cur: entries.append(cur)
        cur = {"key": m.group(1).strip(), "verdict": m.group(2), "judge": "", "advice": ""}
        continue
    if cur is not None and ln.strip():
        if ln.startswith("判斷："):
            cur["judge"] = ln[3:].strip()
        elif ln.startswith("建議："):
            cur["advice"] = ln[3:].strip()
        else:
            cur["judge"] += ln.strip()
if cur: entries.append(cur)
assert len(entries) == 448, len(entries)

# ---------- 2. 存疑 files ----------
def item_id(s):
    m = re.search(r"(\d{3,4})(?:-(\d{4}))?", s)
    if not m: return None
    return m.group(1) + ("-" + m.group(2) if m.group(2) else "")

su_items = []
files = []
for sub in ("r2_存疑", "r3_存疑"):
    d = os.path.join(SU, sub)
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".md"):
            files.append((sub, fn, os.path.join(d, fn)))

for sub, fn, p in files:
    lines = rd(p).split("\n")
    h2 = None          # dict for current H2 section
    def close_h2():
        if h2 and h2["body"].strip():
            su_items.append({"id": item_id(h2["head"]), "key_raw": h2["head"],
                             "text": h2["body"].strip(), "src": f"{sub}/{fn}", "form": "h2",
                             "line": h2["head"]})
    for ln in lines:
        s = ln.rstrip()
        if s.startswith("## "):
            close_h2()
            h2 = {"head": s[3:].strip(), "body": ""}
            continue
        if re.match(r"^\d+\.\s", s) or s.startswith("- **"):
            close_h2()
            if h2: h2 = None
            txt = s.strip()
            txt = re.sub(r"^\d+\.\s*", "", txt)
            txt = re.sub(r"^-\s*", "", txt)
            su_items.append({"id": item_id(txt), "key_raw": txt, "text": "",
                             "src": f"{sub}/{fn}", "form": "line", "line": txt})
            continue
        if h2 is not None:
            h2["body"] += s + "\n"
    close_h2()

print("re0 entries", len(entries))
print("su items", len(su_items))
from collections import Counter
print(Counter(i["form"] for i in su_items))

# ---------- 3. matching ----------
def norm(s):
    s = s.replace("「", "").replace("」", "").replace("『", "").replace("』", "")
    s = s.replace("（", "(").replace("）", ")").replace("〔", "[").replace("〕", "]")
    return re.sub(r"\s+", "", s)

by_id = {}
for it in su_items:
    if it["id"]:
        by_id.setdefault(it["id"], []).append(it)

report, unmatched = [], []
for e in entries:
    if e["verdict"] != "材料不足":
        continue
    k = e["key"]
    tid = item_id(k)
    qs = re.findall(r"「([^」]+)」", k)
    pick, how = None, ""
    cands = by_id.get(tid, []) if tid else []
    if len(cands) == 1:
        pick, how = cands[0], "id"
    elif len(cands) > 1:
        for c in cands:
            t = c["key_raw"] + c["text"]
            if qs and all(q in t for q in qs):
                pick, how = c, "id+quote"; break
        if pick is None:
            pick, how = cands[0], "id-first"
    if pick is None:
        for it in su_items:
            t = it["key_raw"] + "\n" + it["text"]
            if qs and all(q in t for q in qs):
                pick, how = it, "quote"; break
    if pick is None and tid:
        # bare number match: e.g. tid '302' appears as "**302**"
        for it in su_items:
            if it["id"] == tid:
                pick, how = it, "bare"; break
    report.append({"key": k, "tid": tid or "", "found": bool(pick), "how": how,
                   "src": pick["src"] if pick else "", "form": pick["form"] if pick else "",
                   "match_line": pick["line"] if pick else ""})
    if not pick:
        unmatched.append(k)

with open(os.path.join(OUT, "match_report.tsv"), "w", encoding="utf-8") as f:
    f.write("re0key\ttid\tfound\thow\tsrc\tform\tmatch\n")
    for r in report:
        f.write("\t".join([r["key"], r["tid"], str(r["found"]), r["how"], r["src"], r["form"],
                           r["match_line"].replace("\t", " ")[:300]]) + "\n")
print("材料不足", len(report), "unmatched", len(unmatched))
with open(os.path.join(OUT, "unmatched.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(unmatched))
json.dump({"entries": entries, "su_items": su_items},
          open(os.path.join(OUT, "parsed.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
