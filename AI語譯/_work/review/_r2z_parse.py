# -*- coding: utf-8 -*-
"""Parse batch_qwen/r2/resp_*.txt, extract 資持記 entries into JSON."""
import os, re, json, glob, io

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
SRC = os.path.join(ROOT, "batch_qwen", "r2")
OUT = os.path.join(ROOT, "AI語譯", "_work", "review", "_r2z_items.json")
MANIFEST = os.path.join(ROOT, "AI語譯", "_work", "review", "_r2z_manifest.json")

HDR = re.compile(r"^##\s*【(\d+-\d+)】\s*([^/\s]+)/([^#\s]+)#(\d+)\s*$")
QNUM = re.compile(r"^\*\*(\d+)\.\s*(.+?)\*\*\s*$")

def parse_file(path):
    with io.open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    entries = []
    cur = None
    q = None
    for raw in lines:
        line = raw.rstrip("\r")
        m = HDR.match(line.strip())
        if m:
            cur = {"gid": m.group(1), "book": m.group(2), "chunk": m.group(3),
                   "seg": int(m.group(4)), "qs": []}
            entries.append(cur)
            q = None
            continue
        if cur is None:
            continue
        s = line.strip()
        if s == "---":
            q = None
            continue
        if s.startswith("## "):
            cur = None
            q = None
            continue
        mq = QNUM.match(s)
        if mq:
            title = mq.group(2)
            q = {"n": int(mq.group(1)), "title": title,
                 "star": "★" in title, "stars": title.count("★"),
                 "problem": [], "fix": []}
            cur["qs"].append(q)
            continue
        if q is None:
            continue
        if s.startswith("- 問題："):
            q["problem"].append(s[len("- 問題："):])
        elif s.startswith("- 建議改法："):
            q["fix"].append(s[len("- 建議改法："):])
        elif s.startswith("- ") and not q["fix"]:
            q["problem"].append(s[2:])
        elif s.startswith("- ") and q["fix"]:
            q["fix"].append(s[2:])
        elif s and q["fix"]:
            # continuation line
            q["fix"].append(s)
        elif s and q["problem"] and not q["fix"]:
            q["problem"].append(s)
    for e in entries:
        for q in e["qs"]:
            q["problem"] = "\n".join(q["problem"]).strip()
            q["fix"] = "\n".join(q["fix"]).strip()
    return entries

def main():
    files = sorted(glob.glob(os.path.join(SRC, "resp_*.txt")))
    manifest = []
    all_entries = []
    for p in files:
        st = os.stat(p)
        manifest.append({"file": os.path.basename(p), "size": st.st_size,
                         "mtime": st.st_mtime})
        try:
            for e in parse_file(p):
                e["file"] = os.path.basename(p)
                all_entries.append(e)
        except Exception as ex:
            manifest[-1]["error"] = str(ex)
    zc = [e for e in all_entries if e["book"] == "資持記"]
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(zc, f, ensure_ascii=False, indent=1)
    with io.open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print("files:", len(files), "entries:", len(all_entries), "zhichi:", len(zc),
          "zhichi files:", len(set(e["file"] for e in zc)),
          "questions:", sum(len(e["qs"]) for e in zc))
    # book census
    from collections import Counter
    c = Counter(e["book"] for e in all_entries)
    print(c.most_common())

main()
