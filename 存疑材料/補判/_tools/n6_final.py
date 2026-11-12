# -*- coding: utf-8 -*-
"""Step 3 (v3): locate 存疑 items by CONTENT in TXT_分卷, map to out index via 校閱 delta."""
import os, re, json, sys, io
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SU = os.path.join(ROOT, "存疑材料")
TOOLS = os.path.join(SU, "補判", "_tools")
def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()
norm = lambda s: re.sub(r"\s+", "", s)

P = json.load(open(os.path.join(TOOLS, "n1_parsed.json"), encoding="utf-8"))
items, judged_base = P["items"], P["judged_base"]

HDR = re.compile(r"^【(\d{3,4}-\d{4})】 *(.+)$", re.M)
SRC = re.compile(r"【原文】(.*?)(?=\n【譯文】|$)", re.S)
TRA = re.compile(r"【譯文】(.*)", re.S)
chunk_map, chunk_split = {}, {}
for sub in ("校閱_10K", "校閱_20K", "校閱_40K"):
    d = os.path.join(ROOT, sub)
    if not os.path.isdir(d):
        continue
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".txt"):
            continue
        t = rd(os.path.join(d, fn))
        ms = list(HDR.finditer(t))
        for i, m in enumerate(ms):
            end = ms[i + 1].start() if i + 1 < len(ms) else len(t)
            mm = re.match(r"^(.+?)/([^#]+)#(\d+)", m.group(2).strip())
            if not mm:
                continue
            book, chunk, seg = mm.group(1), mm.group(2), int(mm.group(3))
            k = (book, chunk)
            if chunk_split.get(k, sub) != sub:
                continue
            blk = t[m.end():end]
            sm = SRC.search(blk)
            chunk_map.setdefault(k, {})[seg] = sm.group(1).strip() if sm else ""
            chunk_split[k] = sub

def chunk_dir(book):
    if book == "03_業疏":
        return os.path.join(ROOT, "TXT_分卷_標點", book)
    if book == "資持記":
        return os.path.join(ROOT, "TXT_分卷", "資持記_細分")
    return os.path.join(ROOT, "TXT_分卷", book)

def find_file(d, chunk):
    if not os.path.isdir(d):
        return None
    for f in sorted(os.listdir(d)):
        if f.startswith(chunk) and f.endswith(".txt"):
            return os.path.join(d, f)
    return None

_tp, _op = {}, {}
def txt_paras(book, chunk):
    k = (book, chunk)
    if k not in _tp:
        p = find_file(chunk_dir(book), chunk)
        _tp[k] = [l.strip() for l in rd(p).split("\n") if l.strip()] if p else None
    return _tp[k]

def out_paras(book, chunk):
    k = (book, chunk)
    if k not in _op:
        p = find_file(os.path.join(ROOT, "AI語譯", "out", book), chunk)
        _op[k] = [l.strip() for l in rd(p).split("\n") if l.strip()] if p else None
    return _op[k]

# delta + consistency per chunk
delta, dconf = {}, {}
for (book, chunk), segs in chunk_map.items():
    ps = txt_paras(book, chunk)
    if not ps:
        continue
    joined, offs, cur = norm("".join(ps)), [], 0
    for p in ps:
        offs.append(cur); cur += len(norm(p))
    ds = []
    for seg, s in segs.items():
        ns = norm(s)
        if not ns:
            continue
        pos = joined.find(ns)
        if pos < 0:
            continue
        a = max(i for i, o in enumerate(offs) if o <= pos)
        ds.append(a - seg)
    if ds:
        c = Counter(ds)
        delta[(book, chunk)], n = c.most_common(1)[0]
        dconf[(book, chunk)] = (n, len(ds))
print("chunks", len(delta), "| delta consistency <90%:", sum(1 for v in dconf.values() if v[0] < v[1] * 0.9))

CHUNK = re.compile(r"([0-9]{2}[a-z]|00_卷首)[_\u4e00-\u9fff]{0,8}\s*(?:#|＃)\s*(\d+)")
SECTION_CHUNK = re.compile(r"([0-9]{2}[a-z]|00_卷首)")
SEGH = re.compile(r"#\s*(\d+)")
BOOKS = ("01_行事鈔", "02_戒疏", "03_業疏", "04_比丘尼鈔", "05_拾毗尼義鈔", "資持記")
ALIAS = {}
for bk in BOOKS:
    d = chunk_dir(bk)
    if not os.path.isdir(d):
        continue
    for f in os.listdir(d):
        if f.endswith(".txt"):
            ALIAS.setdefault((bk, f.split("_")[0]), f[:-4])

BAD = re.compile(r"[…\.\(\)（）\*]|〔|〕|按：|待考|未改")
def terms_of(it):
    ts = []
    m = re.search(r"原文[^\n：:]{0,6}[：:]\s*`([^`]{4,})`", it["body"])
    if not m:
        m = re.search(r"原文[^\n：:]{0,6}[：:]\s*([^\n`]{4,})", it["body"])
    if m:
        ts.append(m.group(1).strip().strip("「」"))
    for q in re.findall(r"「([^」]{2,30})」", it["raw"]):
        if not BAD.search(q):
            ts.append(q)
    if not ts:
        body = re.sub(r"^\s*\d{3,4}(-\d{4})?\s*[：:]?", "", it["body"])
        runs = [r for r in re.findall(r"[\u4e00-\u9fff]{3,12}", body) if not BAD.search(r)]
        if runs:
            ts = [max(runs, key=len)]
    # dedupe, prefer long
    out = []
    for t in ts:
        t = t.strip()
        if len(t) >= 2 and t not in out:
            out.append(t)
    out.sort(key=lambda x: -len(x))
    return out[:4]

resolved, unresolved = [], []
stats = Counter()
seen = {}

# 校閱 原文 per 段號 (for cross-checked direct hit)
_kj = {}

def kj_src(key):
    if key in _kj:
        return _kj[key]
    num = key.split("-")[0]
    p = os.path.join(ROOT, "校閱_10K", f"校閱_{num}.txt")
    _kj[key] = ""
    if os.path.exists(p):
        t = rd(p)
        i = t.find(f"【{key}】")
        if i >= 0:
            seg = t[i:]
            m = re.search(r"\n【\d{3,4}-\d{4}】", seg[10:])
            end = (m.start() + 10) if m else len(seg)
            blk = seg[:end]
            sm = SRC.search(blk)
            if sm:
                _kj[key] = sm.group(1).strip()
    return _kj[key]

for it in items:
    if re.search(r"ratio|force|待套用", it["raw"]):
        stats["note"] += 1
        continue
    bk = it.get("book_guess")
    if not bk:
        for b in BOOKS:
            if b in it["body"] or b in it["raw"]:
                bk = b
                break
        bk = bk or "04_比丘尼鈔"
    terms = terms_of(it)
    if not terms:
        unresolved.append({"raw": it["raw"], "body": it["body"], "src": it["src"],
                           "section": it.get("section", ""), "terms": [],
                           "files": it.get("files", []), "reason": "無可檢索的引文"})
        continue

    cand = None
    # --- A: 段號 -> 校閱 record, verified by quoted term ---
    ids = [k for k in (it.get("ids") or []) if k in P["seg_index"]]
    for key in ids:
        v = P["seg_index"][key]
        s_kj = kj_src(key)
        if not s_kj:
            continue
        if not any(t in s_kj for t in terms if len(t) >= 3):
            continue
        ck = (v["book"], v["chunk"])
        ps = txt_paras(v["book"], v["chunk"])
        if not ps:
            continue
        para = None
        joined, offs, cur = norm("".join(ps)), [], 0
        for p in ps:
            offs.append(cur); cur += len(norm(p))
        pos = joined.find(norm(s_kj))
        if pos >= 0:
            para = max(i for i, o in enumerate(offs) if o <= pos)
        if para is None or v["seg"] - 1 >= len(out_paras(v["book"], v["chunk"]) or []):
            continue
        cand = (v["book"], v["chunk"], para, v["seg"], "seg-verified")
        stats["seg-verified"] += 1
        break

    if not cand:
        m = CHUNK.search(it["raw"]) or CHUNK.search(it["body"])
        hint_chunk = ALIAS.get((bk, m.group(1))) if m else None
        if not hint_chunk:
            s = SECTION_CHUNK.search(it.get("section") or "")
            if s:
                hint_chunk = ALIAS.get((bk, s.group(1)))
        scopes = [hint_chunk] if hint_chunk else []

        def scan(chunk):
            ps = txt_paras(bk, chunk)
            if not ps:
                return []
            res = []
            for i, txt in enumerate(ps):
                hits = [t for t in terms if t in txt]
                if hits:
                    res.append((i, max(len(t) for t in hits), len(hits)))
            return res

        best = None
        for ch in scopes:
            for i, tlen, nhit in scan(ch):
                score = (tlen, nhit)
                if best is None or score > best[0]:
                    best = (score, ch, i)
        if best and (best[0][0] >= 4 or best[0][1] >= 2):
            best = (best[0], best[1], best[2], "chunk")
        else:
            best = None
        if not best:
            d = chunk_dir(bk)
            allr = []
            if os.path.isdir(d):
                for f in sorted(os.listdir(d)):
                    if not f.endswith(".txt"):
                        continue
                    for i, tlen, nhit in scan(f[:-4]):
                        allr.append(((tlen, nhit), f[:-4], i))
            if allr:
                allr.sort(key=lambda x: x[0], reverse=True)
                if allr[0][0][0] >= 4 or allr[0][0][1] >= 2:
                    best = (allr[0][0], allr[0][1], allr[0][2], "book")
                    stats["book"] += 1
                    if len(allr) > 1 and allr[0][0] == allr[1][0]:
                        stats["book-tie"] += 1
        if best:
            score, ch, i, how = best
            seg = i - delta.get((bk, ch), 0)
            cand = (bk, ch, i, seg, how)
            stats[how] += 1

    if not cand:
        unresolved.append({"raw": it["raw"], "body": it["body"], "src": it["src"],
                           "section": it.get("section", ""), "terms": terms[:2],
                           "files": it.get("files", []), "reason": "引文在原文中找不到"})
        continue

    b2, chunk, para, seg, how = cand
    bk = b2
    ps = txt_paras(bk, chunk)
    ops = out_paras(bk, chunk)
    src = ps[para]
    tra = ops[seg - 1] if ops and 1 <= seg <= len(ops) else ""
    if not tra:
        stats["no-tra"] += 1
        tra = ""

    label = None
    if ids:
        label = ids[0]
    if not label:
        f = (it.get("files") or [None])[0]
        label = (f + "-" + str(seg).zfill(4)) if f else f"{bk.split('_')[0]}-{chunk.split('_')[0]}#{seg}"
    if label in judged_base:
        stats["judged"] += 1
        continue
    if label in seen:
        stats["dup"] += 1
        t = seen[label]
        if it["src"] not in t["srcs"]:
            t["srcs"].append(it["src"])
        t["notes"].append({"raw": it["raw"], "body": it["body"], "src": it["src"]})
        continue
    rec = {"label": label, "book": bk, "chunk": chunk, "seg": seg, "para": para,
           "how": how, "src": src, "tra": tra, "srcs": [it["src"]],
           "section": it.get("section", ""), "siblings": it.get("siblings", []),
           "notes": [{"raw": it["raw"], "body": it["body"], "src": it["src"]}]}
    seen[label] = rec
    resolved.append(rec)
    stats["ok"] += 1

print("resolved", len(resolved), "unresolved", len(unresolved))
print(dict(stats))
print("books", Counter(r["book"] for r in resolved))
json.dump({"resolved": resolved, "unresolved": unresolved},
          open(os.path.join(TOOLS, "n3_final.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\n--- spot check ---")
for r in resolved[:5] + [x for x in resolved if x["label"] in ("003-0001", "004-0003")]:
    print(f"  {r['label']:12s} {r['book']}/{r['chunk']}#{r['seg']} how={r['how']}")
    print("    src:", r["src"][:60])
    print("    tra:", r["tra"][:60])
