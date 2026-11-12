# -*- coding: utf-8 -*-
"""Step 2 (v2): resolve 存疑 items -> (book, chunk, seg); fetch 原文(TXT_分卷)/譯文(out)."""
import os, re, json, sys, io, difflib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SU = os.path.join(ROOT, "存疑材料")
TOOLS = os.path.join(SU, "補判", "_tools")
def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()
norm = lambda s: re.sub(r"\s+", "", s)
def sim(a, b):
    a, b = norm(a), norm(b)
    return difflib.SequenceMatcher(None, a, b).ratio() if a and b else 0.0

P = json.load(open(os.path.join(TOOLS, "n1_parsed.json"), encoding="utf-8"))
items, judged_base, seg_index = P["items"], P["judged_base"], P["seg_index"]

# chunk-name aliases: '04b' -> '04b_上三'
chunk_alias = {}
for k, v in seg_index.items():
    pre = v["chunk"].split("_")[0]
    chunk_alias.setdefault((v["book"], pre), set()).add(v["chunk"])
chunk_alias = {k: next(iter(s)) for k, s in chunk_alias.items() if len(s) == 1}
loc_index = {}
for k, v in seg_index.items():
    loc_index[(v["book"], v["chunk"], v["seg"])] = k
file_segs = {}
for k, v in seg_index.items():
    file_segs.setdefault(k.split("-")[0], []).append(k)

CHUNK = re.compile(r"(?<![\d])([0-9]{2}[a-z]|00_卷首)\s*(?:#|＃)\s*(\d+)")
SEGH = re.compile(r"#\s*(\d+)")

def chunk_dir(book):
    if book == "03_業疏":
        return os.path.join(ROOT, "TXT_分卷_標點", book)
    if book == "資持記":
        return os.path.join(ROOT, "TXT_分卷", "資持記_細分")
    return os.path.join(ROOT, "TXT_分卷", book)

def find_file(d, chunk):
    if not os.path.isdir(d):
        return None
    c = sorted(f for f in os.listdir(d) if f.startswith(chunk) and f.endswith(".txt"))
    return os.path.join(d, c[0]) if c else None

_para, _out, _kj = {}, {}, {}
def txt_paras(book, chunk):
    k = (book, chunk)
    if k not in _para:
        p = find_file(chunk_dir(book), chunk)
        _para[k] = [l.strip() for l in rd(p).split("\n") if l.strip()] if p else None
    return _para[k]

def out_paras(book, chunk):
    k = (book, chunk)
    if k not in _out:
        p = find_file(os.path.join(ROOT, "AI語譯", "out", book), chunk)
        _out[k] = [l.strip() for l in rd(p).split("\n") if l.strip()] if p else None
    return _out[k]

def kj_rec(key):
    """校閱 record -> (原文, 譯文)."""
    if key in _kj:
        return _kj[key]
    num = key.split("-")[0]
    p = os.path.join(ROOT, "校閱_10K", f"校閱_{num}.txt")
    t = rd(p) if os.path.exists(p) else ""
    i = t.find(f"【{key}】")
    src = tra = ""
    if i >= 0:
        seg = t[i:]
        m = re.search(r"\n【\d{3,4}-\d{4}】", seg[10:])
        end = (m.start() + 10) if m else len(seg)
        blk = seg[:end]
        m1 = re.search(r"【原文】(.*?)(?=\n【譯文】|$)", blk, re.S)
        m2 = re.search(r"【譯文】(.*)", blk, re.S)
        src = m1.group(1).strip() if m1 else ""
        tra = m2.group(1).strip() if m2 else ""
    _kj[key] = (src, tra)
    return _kj[key]

def src_span(book, chunk, seg, key):
    src_kj, _ = kj_rec(key)
    paras = txt_paras(book, chunk)
    if not paras:
        return src_kj, "kj-only(no txt file)"
    joined, offs, cur = norm("".join(paras)), [], 0
    for p in paras:
        offs.append(cur); cur += len(norm(p))
    ns = norm(src_kj)
    if not ns:
        return "", "empty"
    pos = joined.find(ns)
    if pos < 0:
        return src_kj, "kj-only(text not in txt)"
    a = max(i for i, o in enumerate(offs) if o <= pos)
    b = max(i for i, o in enumerate(offs) if o <= pos + len(ns) - 1)
    return (paras[a] if a == b else "".join(paras[a:b + 1])), ("txt" if a == b else "txt-join")

def resolve(it):
    raw, body = it["raw"], it["body"]
    ids = [k for k in (it.get("ids") or [])]
    ids = [k for k in ids if k in seg_index]
    if ids:
        return ids[0], "id"
    ch = CHUNK.search(raw) or CHUNK.search(body)
    bk = it.get("book_guess")
    if ch and bk:
        chunk = chunk_alias.get((bk, ch.group(1)))
        if chunk and (bk, chunk, int(ch.group(2))) in loc_index:
            return loc_index[(bk, chunk, int(ch.group(2)))], "chunk#seg"
    sh = SEGH.search(raw) or SEGH.search(body)
    if it.get("files") and sh:
        f = it["files"][0]
        cands = file_segs.get(f, [])
        chunks = {(seg_index[k]["book"], seg_index[k]["chunk"]) for k in cands}
        qs = [q for q in it["quotes"] if len(q) >= 2]
        for b2, c2 in chunks:
            k2 = loc_index.get((b2, c2, int(sh.group(1))))
            if not k2:
                continue
            if not qs or any(q in kj_rec(k2)[0] for q in qs):
                return k2, "file+seg"
        if len(chunks) == 1 and len(cands) == 1:
            return cands[0], "file-only"
    # quote search
    qs = [q for q in it["quotes"] if len(q) >= 3]
    if qs:
        books = [bk] if bk else sorted({v["book"] for v in seg_index.values()})
        hits = []
        for k, v in seg_index.items():
            if v["book"] not in books:
                continue
            s = kj_rec(k)[0]
            if s and all(q in s for q in qs[:2]):
                hits.append(k)
        if len(hits) == 1:
            return hits[0], "quote"
        if hits:
            return hits[0], f"quote({len(hits)})"
    return None, ""

resolved, unresolved, seen = [], [], {}
stats = {"judged": 0, "dup": 0, "ok": 0, "no-src": 0, "no-tra": 0}
for it in items:
    if re.search(r"ratio|force|待套用", it["raw"]):
        unresolved.append({**{k: it[k] for k in ("raw", "body", "src")}, "reason": "非疑點（流程註記）"})
        continue
    key, how = resolve(it)
    if not key:
        reason = "段號僅至檔案層級且無法定位" if it.get("files") else "無段號且引文無法唯一定位"
        unresolved.append({**{k: it[k] for k in ("raw", "body", "src")},
                           "reason": reason, "files": it.get("files", [])})
        continue
    if key in judged_base:
        stats["judged"] += 1
        continue
    if key in seen:
        stats["dup"] += 1
        t = seen[key]
        if it["src"] not in t["srcs"]:
            t["srcs"].append(it["src"])
        t["notes"].append({"raw": it["raw"], "body": it["body"], "src": it["src"]})
        continue
    v = seg_index[key]
    src, sh_how = src_span(v["book"], v["chunk"], v["seg"], key)
    ops = out_paras(v["book"], v["chunk"])
    tra = ops[v["seg"] - 1] if ops and v["seg"] - 1 < len(ops) else ""
    kj_tra = kj_rec(key)[1]
    rec = {"key": key, "book": v["book"], "chunk": v["chunk"], "seg": v["seg"],
           "src": src, "src_how": sh_how, "tra": tra, "how": how,
           "tra_sim": round(sim(tra, kj_tra), 2),
           "srcs": [it["src"]], "siblings": it.get("siblings", []),
           "notes": [{"raw": it["raw"], "body": it["body"], "src": it["src"]}]}
    if not src.strip():
        stats["no-src"] += 1
    if not tra.strip():
        stats["no-tra"] += 1
    seen[key] = rec
    resolved.append(rec)
    stats["ok"] += 1

from collections import Counter
print("resolved", len(resolved), "unresolved", len(unresolved), stats)
print("src_how", Counter(r["src_how"] for r in resolved))
print("how", Counter(r["how"] for r in resolved))
print("books", Counter(r["book"] for r in resolved))
lowsim = [r for r in resolved if r["tra_sim"] < 0.5]
print("tra_sim<0.5:", len(lowsim))
for r in lowsim[:8]:
    print("  ", r["key"], r["book"], r["chunk"], r["seg"], r["tra_sim"], r["tra"][:40])

json.dump({"resolved": resolved, "unresolved": unresolved},
          open(os.path.join(TOOLS, "n2_resolved.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("wrote n2_resolved.json")
print("\n--- unresolved by reason ---")
for why, n in Counter(u["reason"] for u in unresolved).most_common():
    print(f"  {n:3d}  {why}")
