# -*- coding: utf-8 -*-
"""Resolve 材料不足 entries: book-aware + text-scored 校閱 candidate selection."""
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
        m = re.search(r"/([0-9]{2}[a-f]|00_卷首)[^#]*#(\d+)", label)
        out.append({"code": code, "label": label, "book": label.split("/")[0],
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
def paras(book, chunkpfx):
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

    if pick is None and iid and "-" in iid:
        for it in su:
            if iid in it["key_raw"]:
                pick = it; break
    srcfile = pick["src"] if pick else ""
    book = srcfile.split("/")[-1].replace(".md", "") if srcfile else None
    if book not in BOOKS: book = None
    hdr = pick["key_raw"] if pick else ""
    note = (pick["key_raw"] + "\n" + pick["text"]) if pick else ""

    chunk = seg = None
    for s in (k, hdr):
        m = CHUNK_RE.search(s)
        if m: chunk, seg = m.group(1), int(m.group(2)); break
    if seg is None:
        m = SEG_RE.search(kk) or SEG_RE.search(hdr)
        if m: seg = int(m.group(1))

    # candidates from 校閱 by code (book aware) or by number+seg
    candlist = []
    if book and iid:
        it = by_code.get((book, iid))
        if it: candlist.append(it)
    if book and seg is not None:
        n = (rawid or "").split("-")[0]
        for it in by_num.get((book, n), []):
            if it["seg"] == seg and it not in candlist:
                candlist.append(it)
        if chunk:
            it = by_lbl.get((book, chunk, seg))
            if it and it not in candlist: candlist.append(it)

    # score candidates: tag hits in src+tr + current paragraph
    def score(it):
        t = it["src"] + it["tr"]
        s = sum(len(tg) for tg in tags if tg and tg in t)
        if it["chunk"] and it["seg"]:
            c = paras(book, it["chunk"])
            if c and 1 <= it["seg"] <= len(c["paras"]):
                s += 2 * sum(len(tg) for tg in tags if tg and tg in c["paras"][it["seg"] - 1])
        return s

    item = None
    if candlist:
        item = max(candlist, key=score)
        if chunk is None or seg is None:
            chunk, seg = item["chunk"], item["seg"]
    if item and (not chunk or seg is None):
        chunk, seg = item["chunk"], item["seg"]

    # text fallback: locate seg by scanning book chunks for tags in current 譯文
    if (not chunk or seg is None) and book and tags:
        best = None
        d = os.path.join(OUTJ, book)
        for fn in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if not fn.endswith(".txt"): continue
            ps = [l for l in rd(os.path.join(d, fn)).split("\n") if l.strip()]
            for i, l in enumerate(ps):
                sc = sum(len(tg) for tg in tags if tg and tg in l)
                if sc >= 4 and (best is None or sc > best[0]):
                    best = (sc, fn.split("_")[0], i + 1, l)
        if best and best[0] >= 4:
            chunk, seg = best[1], best[2]
            if not item:
                item = by_lbl.get((book, chunk, seg))

    src = (item or {}).get("src", "") or ""
    if not src and book and chunk and seg:
        src = (by_lbl.get((book, chunk, seg)) or {}).get("src", "")
    cur = ""
    if book and chunk and seg:
        c = paras(book, chunk)
        if c and 1 <= seg <= len(c["paras"]): cur = c["paras"][seg - 1]

    rows.append({"key": k, "iid": iid, "srcfile": srcfile, "book": book, "chunk": chunk, "seg": seg,
                 "src": src, "cur": cur, "su_note": note, "su_raw": hdr,
                 "judge": e["judge"], "advice": e["advice"],
                 "kjcode": (item or {}).get("code", "")})

json.dump(rows, open(os.path.join(TOOLS, "resolved4.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print({"total": len(rows), "src": sum(1 for r in rows if r["src"]), "cur": sum(1 for r in rows if r["cur"]),
       "both": sum(1 for r in rows if r["src"] and r["cur"])})
miss = [f'{r["key"]}\t{r["book"]}\t{r["chunk"]}#{r["seg"]}\tsrc={bool(r["src"])}\tcur={bool(r["cur"])}'
        for r in rows if not (r["src"] and r["cur"])]
open(os.path.join(TOOLS, "resolve_missing4.txt"), "w", encoding="utf-8").write("\n".join(miss))
print("incomplete", len(miss))
