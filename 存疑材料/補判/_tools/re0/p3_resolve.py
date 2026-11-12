# -*- coding: utf-8 -*-
"""Resolve each 材料不足 entry to (book, chunk, seg) + 原文 + 現行譯文."""
import os, re, json, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SU = os.path.join(ROOT, "存疑材料")
TOOLS = os.path.join(SU, "補判", "_tools")
OUTJ = os.path.join(ROOT, "AI語譯", "out")

def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

data = json.load(open(os.path.join(TOOLS, "parsed.json"), encoding="utf-8"))
entries = data["entries"]
su = data["su_items"]
kj = json.load(open(os.path.join(TOOLS, "kj_index.json"), encoding="utf-8"))

BOOKS = ["01_行事鈔", "02_戒疏", "03_業疏", "04_比丘尼鈔", "05_拾毗尼義鈔", "資持記"]
FILE_BOOK = {"01_行事鈔": "01_行事鈔", "02_戒疏": "02_戒疏", "03_業疏": "03_業疏",
             "04_比丘尼鈔": "04_比丘尼鈔", "05_拾毗尼義鈔": "05_拾毗尼義鈔", "資持記": "資持記",
             "其他三書": None}

# chunk cache: book -> chunk prefix -> list of paragraphs
chunk_cache = {}
def chunk_paras(book, chunkpfx):
    key = (book, chunkpfx)
    if key in chunk_cache:
        return chunk_cache[key]
    d = os.path.join(OUTJ, book)
    if not os.path.isdir(d):
        chunk_cache[key] = None; return None
    cand = [f for f in os.listdir(d) if f.startswith(chunkpfx) and f.endswith(".txt")]
    if not cand:
        chunk_cache[key] = None; return None
    p = os.path.join(d, cand[0])
    paras = [l for l in rd(p).split("\n") if l.strip()]
    chunk_cache[key] = {"file": cand[0], "paras": paras}
    return chunk_cache[key]

def item_id(s):
    m = re.search(r"(\d{3,4})(?:-(\d{4}|#\d{1,2}))?", s)
    if not m: return None
    if m.group(2):
        g = m.group(2)
        return m.group(1) + ("-" + g if g.startswith("#") else "-" + g)
    return m.group(1)

def norm_id(s):
    """normalise to NNNN-#### form where possible"""
    if not s: return None
    m = re.match(r"^(\d{3,4})-(#?)(\d{1,4})$", s)
    if m:
        return f"{m.group(1)}-{int(m.group(3)):04d}"
    return s

by_id = {}
for it in su:
    i = item_id(it["key_raw"])
    if i:
        by_id.setdefault(norm_id(i), []).append(it)

CHUNK_RE = re.compile(r"([0-9]{2}[a-f]|00_卷首)(?:[^#）)]*)?#(\d{1,3})")

def parse_chunkseg(s):
    m = CHUNK_RE.search(s)
    if m:
        return m.group(1), int(m.group(2))
    return None, None

rows = []
for e in entries:
    if e["verdict"] != "材料不足":
        continue
    k = e["key"]
    iid = norm_id(item_id(k))
    # locate 存疑 item
    cands = by_id.get(iid, [])
    tags = re.findall(r"「([^」]+)」", k) + [t for t in re.findall(r"（([^）]+)）", k) if "#" not in t]
    pick = None
    if cands:
        if len(cands) == 1:
            pick = cands[0]
        else:
            best, bs = None, -1
            for c in cands:
                t = c["key_raw"] + c["text"]
                sc = sum(1 for tg in tags if tg and tg in t)
                if sc > bs:
                    best, bs = c, sc
            pick = best
    if pick is None:
        # literal id search (bundled lines)
        lit = re.match(r"^(\d{3,4}(?:-\d{4}|-#\d{1,2})?)", k)
        if lit:
            base = lit.group(1).split("#")[0]
            for it in su:
                if lit.group(1) in it["key_raw"] or (base in it["key_raw"] and any(t in it["key_raw"] for t in tags)):
                    pick = it; break
    if pick is None and tags:
        for it in su:
            t = it["key_raw"] + it["text"]
            if all(tg in t for tg in tags):
                pick = it; break

    srcfile = pick["src"] if pick else ""
    book = FILE_BOOK.get(srcfile.split("/")[-1].replace(".md", ""), None)
    raw = (pick["key_raw"] + "\n" + pick["text"]) if pick else ""

    # chunk/seg: 1) from re0 key parenthetical; 2) from 存疑 header; 3) from 校閱 label
    chunk, seg = parse_chunkseg(k)
    if not chunk:
        chunk, seg = parse_chunkseg(pick["key_raw"] if pick else "")
    kjitem = kj.get(iid) or kj.get(norm_id(iid) or "")
    if not kjitem and re.match(r"^\d{3,4}-#\d+$", iid or ""):
        n = iid.split("-")[0]
        want = "#" + iid.split("#")[1]
        for code, it in kj.items():
            if code.startswith(n + "-") and it["label"].endswith(want):
                kjitem = it; break
    if (not chunk or seg is None) and kjitem:
        m = re.search(r"/([0-9]{2}[a-f]|00_卷首)[^#]*#(\d+)", kjitem["label"])
        if m:
            chunk, seg = m.group(1), int(m.group(2))
    if not book and kjitem:
        b = kjitem["label"].split("/")[0]
        book = b if b in BOOKS else None

    cur = None
    if book and chunk and seg:
        c = chunk_paras(book, chunk)
        if c and 1 <= seg <= len(c["paras"]):
            cur = c["paras"][seg - 1]
    rows.append({"key": k, "iid": iid, "srcfile": srcfile, "book": book,
                 "chunk": chunk, "seg": seg,
                 "kj": bool(kjitem), "src_kj": (kjitem or {}).get("src", ""),
                 "tr_kj": (kjitem or {}).get("tr", ""),
                 "cur": cur or "",
                 "su_raw": pick["key_raw"] if pick else "",
                 "su_text": pick["text"] if pick else "",
                 "judge": e["judge"]})

json.dump(rows, open(os.path.join(TOOLS, "resolved.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

stat = {"total": len(rows),
        "has_kj": sum(1 for r in rows if r["kj"]),
        "has_cur": sum(1 for r in rows if r["cur"]),
        "book": sum(1 for r in rows if r["book"])}
print(stat)
miss = [f'{r["key"]}\tbook={r["book"]}\tchunk={r["chunk"]}\tseg={r["seg"]}\tkj={r["kj"]}\tcur={bool(r["cur"])}' for r in rows if not (r["kj"] and r["cur"])]
open(os.path.join(TOOLS, "resolve_missing.txt"), "w", encoding="utf-8").write("\n".join(miss))
print("incomplete", len(miss))
