# -*- coding: utf-8 -*-
"""Parse 是錯 entries from 回覆 txt + 段號->書/chunk#段 mapping from 新_補_NN.md materials."""
import os, re, json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
REP = os.path.join(ROOT, "存疑材料", "補判", "回覆")
MAT = os.path.join(ROOT, "存疑材料", "補判")

# reply files, with 回2 priority
FILES = []
for i in range(1, 20):
    n = "新_補_%02d" % i
    p1 = os.path.join(REP, n + "_回.txt")
    p2 = os.path.join(REP, n + "_回2.txt")
    if os.path.exists(p2):
        FILES.append(p2)          # 優先 _回2，忽略 _回
    elif os.path.exists(p1):
        FILES.append(p1)
FILES.append(os.path.join(REP, "末_補_01_回.txt"))

def rd(p):
    with open(p, encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")

HDR = re.compile(r"^###\s*(\S+?)｜(是錯|不是錯|材料不足)\s*$")

entries = []
for p in FILES:
    txt = rd(p)
    lines = txt.split("\n")
    cur = None
    for ln in lines:
        m = HDR.match(ln.strip())
        if m:
            if cur:
                entries.append(cur)
            cur = {"id": m.group(1), "verdict": m.group(2), "judge": "", "sugg": "", "file": os.path.basename(p)}
            continue
        if cur is None:
            continue
        s = ln.strip()
        if s.startswith("判斷："):
            cur["judge"] = s[len("判斷："):]
            cur["sec"] = "judge"
        elif s.startswith("建議："):
            cur["sugg"] = s[len("建議："):]
            cur["sec"] = "sugg"
        elif s and cur.get("sec") == "judge":
            cur["judge"] += s
        elif s and cur.get("sec") == "sugg":
            cur["sugg"] += s
        elif s.startswith("###"):
            pass
    if cur:
        entries.append(cur)

# material mapping
MAP = {}
def parse_mat(path):
    txt = rd(path)
    blocks = re.split(r"^###\s+", txt, flags=re.M)
    for b in blocks[1:]:
        lines = b.split("\n")
        seg = lines[0].strip()
        d = {}
        for ln in lines:
            m = re.match(r"^-\s+\*\*(.+?)\*\*[：:]\s*(.*)$", ln.strip())
            if m:
                d[m.group(1)] = m.group(2)
        if "書/chunk#段" in d:
            MAP[seg] = d["書/chunk#段"]
        MAP.setdefault("#" + seg, {"段號": seg, **d})

for i in range(1, 20):
    parse_mat(os.path.join(MAT, "新_補_%02d.md" % i))
parse_mat(os.path.join(MAT, "末_補_01.md"))

bad = [e for e in entries if e["verdict"] == "是錯"]
print("total entries:", len(entries), "是錯:", len(bad))
missing = [e["id"] for e in bad if e["id"] not in MAP]
print("no material map:", missing)

out = []
for e in bad:
    loc = MAP.get(e["id"], "")
    e["loc"] = loc
    out.append(e)

with open(os.path.join(os.path.dirname(__file__), "m1_bad.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
with open(os.path.join(os.path.dirname(__file__), "m1_all.json"), "w", encoding="utf-8") as f:
    json.dump(entries, f, ensure_ascii=False, indent=1)

for e in out:
    print("-" * 70)
    print(e["id"], "|", e["loc"], "|", e["file"], "| sugg len", len(e["sugg"]))
    print("  判斷:", e["judge"][:200])
