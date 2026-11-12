# -*- coding: utf-8 -*-
"""Resolve each 材料不足 entry to (book, chunk, seg) + 原文 + 現行譯文."""
import os, re, json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SU = os.path.join(ROOT, "存疑材料")
TOOLS = os.path.join(SU, "補判", "_tools")
OUTJ = os.path.join(ROOT, "AI語譯", "out")

def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

data = json.load(open(os.path.join(TOOLS, "parsed.json"), encoding="utf-8"))
entries, su = data["entries"], data["su_items"]
KJ = json.load(open(os.path.join(TOOLS, "kj2.json"), encoding="utf-8"))
idx, bylabel, bynum = KJ["idx"], KJ["bylabel"], KJ["bynum"]

BOOKS = ["01_行事鈔", "02_戒疏", "03_業疏", "04_比丘尼鈔", "05_拾毗尼義鈔", "資持記"]

chunk_cache = {}
def chunk_paras(book, chunkpfx):
    key = (book, chunkpfx)
    if key in chunk_cache:
        return chunk_cache[key]
    d = os.path.join(OUTJ, book)
    r = None
    if os.path.isdir(d):
        cand = sorted(f for f in os.listdir(d) if f.startswith(chunkpfx) and f.endswith(".txt"))
        if cand:
            r = {"file": cand[0], "paras": [l for l in rd(os.path.join(d, cand[0])).split("\n") if l.strip()]}
    chunk_cache[key] = r
    return r

def item_id(s):
    m = re.search(r"(\d{3,4})(?:-(\d{4}|#\d{1,2}))?", s)
    if not m: return None
    return m.group(1) + ("-" + m.group(2) if m.group(2) else "")

def norm(s):
    if not s: return None
    m = re.match(r"^(\d{3,4})-(#?)(\d{1,4})$", s)
    if m:
        return f"{m.group(1)}-{int(m.group(3)):04d}"
    return s

by_id = {}
for it in su:
    i = item_id(it["key_raw"])
    if i: by_id.setdefault(norm(i), []).append(it)

CHUNK_RE = re.compile(r"(?<![0-9f])((?:[0-9]{2}[a-f])|00_卷首)(?:[^#）)]*)?#(\d{1,3})")

rows = []
for e in entries:
    if e["verdict"] != "材料不足":
        continue
    k = e["key"]
    rawid = item_id(re.sub(r"[【】]", "", k))
    iid = norm(rawid)
    tags = re.findall(r"「([^」]+)」", k) + [t for t in re.findall(r"（([^）]+)）", k) if "#" not in t]
    cands = by_id.get(iid, [])
    pick = None
    if cands:
        best, bs = None, -1
        for c in cands:
            t = c["key_raw"] + c["text"]
            sc = sum(1 for tg in tags if tg and tg in t)
            if sc > bs: best, bs = c, sc
        pick = best
    if pick is None:
        lit = re.match(r"^(\d{3,4}(?:-\d{4}|-#\d{1,2})?)", re.sub(r"[【】]", "", k))
        if lit:
            for it in su:
                if lit.group(1) in it["key_raw"]:
                    pick = it; break
    if pick is None and tags:
        for it in su:
            t = it["key_raw"] + it["text"]
            if all(tg in t for tg in tags):
                pick = it; break

    srcfile = pick["src"] if pick else ""
    book = srcfile.split("/")[-1].replace(".md", "") if srcfile else None
    if book not in BOOKS: book = None

    # chunk/seg: key paren, then 存疑 header, then kj code, then bynum label
    chunk, seg = (None, None)
    for s in (k, pick["key_raw"] if pick else ""):
        if not chunk:
            chunk, seg = CHUNK_RE.search(s).group(1, 2) if CHUNK_RE.search(s) else (None, None)
            if seg is not None: seg = int(seg)
    kjitem = idx.get(iid)
    if (not chunk or seg is None) and kjitem:
        m = re.search(r"/([0-9]{2}[a-f]|00_卷首)[^#]*#(\d+)", kjitem["label"])
        if m: chunk, seg = m.group(1), int(m.group(2))
    if (not chunk or seg is None) and rawid and "#" in (rawid or ""):
        n, want = rawid.split("-")
        want = "#" + want.lstrip("#")
        for it in bynum.get(n, []):
            if it["label"].endswith(want):
                kjitem = kjitem or it
                m = re.search(r"/([0-9]{2}[a-f]|00_卷首)[^#]*#(\d+)", it["label"])
                if m: chunk, seg = m.group(1), int(m.group(2))
                break
    if not book and kjitem:
        b = kjitem["label"].split("/")[0]
        book = b if b in BOOKS else None

    src_txt = (kjitem or {}).get("src", "")
    if not src_txt and book and chunk and seg is not None:
        src_txt = (bylabel.get(f"{book}|{chunk}|{seg}") or {}).get("src", "")
    cur = ""
    if book and chunk and seg:
        c = chunk_paras(book, chunk)
        if c and 1 <= seg <= len(c["paras"]):
            cur = c["paras"][seg - 1]

    rows.append({"key": k, "iid": iid, "srcfile": srcfile, "book": book, "chunk": chunk, "seg": seg,
                 "kj": bool(src_txt), "src": src_txt, "cur": cur,
                 "su_raw": (pick["key_raw"] if pick else ""), "su_text": (pick["text"] if pick else ""),
                 "judge": e["judge"], "advice": e["advice"]})

json.dump(rows, open(os.path.join(TOOLS, "resolved.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
st = {"total": len(rows), "src": sum(1 for r in rows if r["src"]),
      "cur": sum(1 for r in rows if r["cur"]),
      "both": sum(1 for r in rows if r["src"] and r["cur"]),
      "cs": sum(1 for r in rows if r["chunk"] and r["seg"])}
print(st)
miss = [f'{r["key"]}\t{r["book"]}\t{r["chunk"]}#{r["seg"]}\tsrc={bool(r["src"])}\tcur={bool(r["cur"])}'
        for r in rows if not (r["src"] and r["cur"])]
open(os.path.join(TOOLS, "resolve_missing.txt"), "w", encoding="utf-8").write("\n".join(miss))
print("incomplete", len(miss))
