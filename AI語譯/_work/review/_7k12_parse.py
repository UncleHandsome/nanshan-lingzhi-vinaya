# -*- coding: utf-8 -*-
"""Parse 校閱_7K/校閱_NNN.txt (397-434) and compare with current out chunks."""
import os, re, json

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT, "AI語譯", "out", "01_行事鈔")
REV = os.path.join(ROOT, "校閱_7K")

FILES = list(range(397, 435))
seg_re = re.compile(r"^【(\d{3})-(\d{4})】(\S+)#(\d+)\s*$")

def load_chunk(name):
    p = os.path.join(OUT, name + ".txt")
    raw = open(p, "rb").read()
    nl = b"\r\n" if b"\r\n" in raw else b"\n"
    txt = raw.decode("utf-8-sig")
    lines = txt.split(nl.decode())
    return lines, nl

def nonempty_idx(lines):
    return [i for i, l in enumerate(lines) if l.strip()]

chunks = {}
def get_chunk(name):
    if name not in chunks:
        lines, nl = load_chunk(name)
        chunks[name] = (lines, nl, nonempty_idx(lines))
    return chunks[name]

result = []
for n in FILES:
    p = os.path.join(REV, "校閱_%d.txt" % n)
    if not os.path.exists(p):
        result.append({"file": n, "missing": True, "segs": []})
        continue
    txt = open(p, encoding="utf-8-sig").read().replace("\r\n", "\n")
    lines = txt.split("\n")
    segs = []
    cur = None
    for ln in lines:
        m = seg_re.match(ln.strip())
        if m:
            if cur: segs.append(cur)
            cur = {"label": "%s-%s" % (m.group(1), m.group(2)), "chunk": m.group(3).split("/")[-1],
                   "idx": int(m.group(4)), "yuanwen": "", "yiwen": ""}
            continue
        if cur is None: continue
        s = ln.strip()
        if s.startswith("【原文】"):
            cur["yuanwen"] = s[4:].strip()
        elif s.startswith("【譯文】"):
            cur["yiwen"] = s[4:].strip()
        elif s and cur["yiwen"]:
            cur["yiwen"] += s
    if cur: segs.append(cur)
    for sg in segs:
        cl, nl, ne = get_chunk(sg["chunk"])
        k = sg["idx"] - 1
        sg["cur"] = cl[ne[k]] if 0 <= k < len(ne) else None
        sg["same"] = (sg.get("cur") == sg["yiwen"])
    result.append({"file": n, "missing": False, "segs": segs})

with open(os.path.join(os.path.dirname(__file__), "_7k12_data.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)

tot = 0
for r in result:
    if r["missing"]:
        print(r["file"], "MISSING 校閱")
        continue
    chg = [s["label"] for s in r["segs"] if not s["same"]]
    tot += len(r["segs"])
    print(r["file"], "segs=%d" % len(r["segs"]), "changed=" + (",".join(chg) if chg else "-"))
print("TOTAL segs:", tot)
