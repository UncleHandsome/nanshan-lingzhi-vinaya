# -*- coding: utf-8 -*-
"""Resolve 材料不足 entries using book-aware 校閱 index."""
import os, re, json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SU = os.path.join(ROOT, "存疑材料")
TOOLS = os.path.join(SU, "補判", "_tools")
OUTJ = os.path.join(ROOT, "AI語譯", "out")

def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

BOOKS = ["01_行事鈔", "02_戒疏", "03_業疏", "04_比丘尼鈔", "05_拾毗尼義鈔", "資持記"]
DIRS = ["校閱_10K", "校閱_20K", "校閱_40K", "校閱_80K"]
data = json.load(open(os.path.join(TOOLS, "parsed.json"), encoding="utf-8"))
entries, su = data["entries"], data["su_items"]

nums = set()
for e in entries:
    if e["verdict"] != "材料不足": continue
    for m in re.finditer(r"(\d{3,4})(?:-\d{4}|-#\d{1,2})?", re.sub(r"[【】]", "", e["key"])):
        nums.add(m.group(1))

def parse_file(p):
    t = rd(p)
    parts = re.split(r"^【(\d{3,4}-\d{4})】(.*)$", t, flags=re.M)
    out = []
    for i in range(1, len(parts) - 1, 3):
        code, label = parts[i], parts[i + 1].strip()
        body = parts[i + 2]
        m2 = re.search(r"【譯文】(.*)", body, re.S)
        tr = m2.group(1).strip() if m2 else ""
        src = body[:m2.start()].strip() if m2 else body.strip()
        b = label.split("/")[0]
        m = re.search(r"/([0-9]{2}[a-f]|00_卷首)[^#]*#(\d+)", label)
        out.append({"code": code, "label": label, "book": b,
                    "chunk": m.group(1) if m else None, "seg": int(m.group(2)) if m else None,
                    "src": src.strip(), "tr": tr})
    return out

by_code, by_lbl, by_num = {}, {}, {}
for d in DIRS:
    base = os.path.join(ROOT, d)
    if not os.path.isdir(base): continue
    for n in sorted(nums):
        p = os.path.join(base, f"校閱_{n}.txt")
        if not os.path.exists(p): continue
        for it in parse_file(p):
            by_code.setdefault((it["book"], it["code"]), it)
            by_num.setdefault((it["book"], n), []).append(it)
            if it["chunk"]:
                by_lbl.setdefault((it["book"], it["chunk"], it["seg"]), it)

chunk_cache = {}
def chunk_paras(book, chunkpfx):
    key = (book, chunkpfx)
    if key not in chunk_cache:
        d = os.path.join(OUTJ, book); r = None
        if os.path.isdir(d):
            cand = sorted(f for f in os.listdir(d) if f.startswith(chunkpfx) and f.endswith(".txt"))
            if cand:
                r = {"file": cand[0], "paras": [l for l in rd(os.path.join(d, cand[0])).split("\n") if l.strip()]}
        chunk_cache[key] = r
    return chunk_cache[key]

def item_id(s):
    m = re.search(r"(\d{3,4})(?:-(\d{4}|#\d{1,2}))?", s)
    return m.group(1) + ("-" + m.group(2) if m.group(2) else "") if m else None

def norm(s):
    if not s: return None
    m = re.match(r"^(\d{3,4})-(#?)(\d{1,4})$", s)
    return f"{m.group(1)}-{int(m.group(3)):04d}" if m else s

by_id = {}
for it in su:
    i = item_id(it["key_raw"])
    if i: by_id.setdefault(norm(i), []).append(it)

CHUNK_RE = re.compile(r"((?:[0-9]{2}[a-f])|00_卷首)[^#）)]*#(\d{1,3})")
SEG_RE = re.compile(r"#(\d{1,3})")

rows = []
for e in entries:
    if e["verdict"] != "材料不足": continue
    k = e["key"]; kk = re.sub(r"[【】]", "", k)
    rawid = item_id(kk); iid = norm(rawid)
    tags = re.findall(r"「([^」]+)」", k) + [t for t in re.findall(r"（([^）]+)）", k) if "#" not in t]
    pick = None
    cands = by_id.get(iid, [])
    if cands:
        pick = max(cands, key=lambda c: sum(1 for tg in tags if tg and tg in c["key_raw"] + c["text"]))
    if pick is None:
        lit = re.match(r"^(\d{3,4}(?:-\d{4}|-#\d{1,2})?)", kk)
        if lit:
            for it in su:
                if lit.group(1) in it["key_raw"]: pick = it; break
    if pick is None and tags:
        for it in su:
            t = it["key_raw"] + it["text"]
            if all(tg in t for tg in tags): pick = it; break

    srcfile = pick["src"] if pick else ""
    book = srcfile.split("/")[-1].replace(".md", "") if srcfile else None
    if book not in BOOKS: book = None
    hdr = pick["key_raw"] if pick else ""

    chunk = seg = None
    for s in (k, hdr):
        m = CHUNK_RE.search(s)
        if m: chunk, seg = m.group(1), int(m.group(2)); break
    if seg is None:
        m = SEG_RE.search(kk) or SEG_RE.search(hdr)
        if m: seg = int(m.group(1))
    item = by_code.get((book, iid)) if book else None
    if item is None:
        for (b, c), it in by_code.items():
            if c == iid: item = it; break
    if item and book and item["book"] != book:
        item = None
    if (not chunk or seg is None) and item and item["chunk"]:
        chunk, seg = item["chunk"], item["seg"]
    if (not chunk or seg is None) and rawid and seg is not None:
        n = rawid.split("-")[0]
        for it in by_num.get((book, n), []) + [x for (b, nn), v in by_num.items() if nn == n for x in v]:
            if it["seg"] == seg:
                item = item or it
                if it["book"] == book: chunk = it["chunk"]
                break
    src = (item or {}).get("src", "") or ""
    if not src and book and chunk and seg:
        src = (by_lbl.get((book, chunk, seg)) or {}).get("src", "")
    cur = ""
    if book and chunk and seg:
        c = chunk_paras(book, chunk)
        if c and 1 <= seg <= len(c["paras"]): cur = c["paras"][seg - 1]

    rows.append({"key": k, "iid": iid, "srcfile": srcfile, "book": book, "chunk": chunk, "seg": seg,
                 "src": src, "cur": cur, "su_raw": pick["key_raw"] if pick else "",
                 "su_text": pick["text"] if pick else "", "judge": e["judge"], "advice": e["advice"]})

json.dump(rows, open(os.path.join(TOOLS, "resolved2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print({"total": len(rows), "src": sum(1 for r in rows if r["src"]), "cur": sum(1 for r in rows if r["cur"]),
       "both": sum(1 for r in rows if r["src"] and r["cur"])})
miss = [f'{r["key"]}\t{r["book"]}\t{r["chunk"]}#{r["seg"]}\tsrc={bool(r["src"])}\tcur={bool(r["cur"])}'
        for r in rows if not (r["src"] and r["cur"])]
open(os.path.join(TOOLS, "resolve_missing2.txt"), "w", encoding="utf-8").write("\n".join(miss))
print("incomplete", len(miss))
