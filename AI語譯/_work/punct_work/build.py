import json, os, glob, re

base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work"
work = os.path.join(base, "punct_work")
MARKS = "\uff0c\u3002\u3001\uff1b\uff1a\uff1f\uff01\u300c\u300d\uff08\uff09"
MSET = set(MARKS)

def nm(s):
    return "".join(c for c in s if c not in MSET)

inp = json.load(open(os.path.join(base, "ys_punct_in.json"), encoding="utf-8"))
ex = json.load(open(os.path.join(work, "v3_extract.json"), encoding="utf-8"))

manual = {}
for f in sorted(glob.glob(os.path.join(work, "p*.txt"))):
    if os.path.basename(f).startswith("punct"):
        continue
    for line in open(f, encoding="utf-8"):
        line = line.rstrip("\n")
        if "\t" not in line:
            continue
        idx, txt = line.split("\t", 1)
        manual[idx.strip()] = txt

texts = {}
src_of = {}
for bi, (k, paras) in enumerate(inp.items()):
    for pi, p in enumerate(paras):
        key = f"{bi}.{pi}"
        cand = ex.get(key)
        chosen = None
        if cand is not None:
            c = cand
            if p.rstrip().endswith(("\u3002", "\uff01", "\uff1f")) and not c.endswith(("\u3002", "\uff01", "\uff1f", "\u300d")):
                c = c + p.rstrip()[-1]
            if nm(c) == nm(p) and "\u3000" not in c:
                chosen = c
                src_of[key] = "v3"
        if chosen is None and key in manual:
            chosen = manual[key]
            src_of[key] = "manual"
        if chosen is not None:
            texts[key] = chosen

missing = [f"{bi}.{pi}" for bi, (k, paras) in enumerate(inp.items()) for pi in range(len(paras)) if f"{bi}.{pi}" not in texts]
print("filled", len(texts), "missing", len(missing))
print("missing:", " ".join(missing))
print("manual count", sum(1 for v in src_of.values() if v == "manual"))

blocks = []
for bi, (k, paras) in enumerate(inp.items()):
    blocks.append({"key": k, "texts": [texts.get(f"{bi}.{pi}", "") for pi in range(len(paras))]})
json.dump({"blocks": blocks}, open(os.path.join(work, "draft.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# long unpunctuated runs
runs = []
for key, t in texts.items():
    for m in re.finditer(r"[^，。、；：？！「」（）]+", t):
        runs.append((len(m.group(0)), key, m.group(0)))
runs.sort(reverse=True)
with open(os.path.join(work, "longruns.txt"), "w", encoding="utf-8") as fh:
    for r in runs[:40]:
        fh.write(f"{r[0]}\t{r[1]}\t{r[2]}\n")
print("wrote draft.json and longruns.txt")
