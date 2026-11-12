# -*- coding: utf-8 -*-
"""Final: resolve NEW 存疑 items -> complete 裁判材料 files 新_補_NN.md."""
import os, re, json, sys, io, difflib, math
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SU = os.path.join(ROOT, "存疑材料")
TOOLS = os.path.join(SU, "補判", "_tools")
BJ = os.path.join(SU, "補判")

def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()
norm = lambda s: re.sub(r"\s+", "", s)
def nkey(s):
    return re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", s)
def sim(a, b):
    a, b = norm(a), norm(b)
    return difflib.SequenceMatcher(None, a, b).ratio() if a and b else 0.0

P = json.load(open(os.path.join(TOOLS, "n1_parsed.json"), encoding="utf-8"))
items, judged_base = P["items"], P["judged_base"]
loc_index = {(v["book"], v["chunk"], v["seg"]): k for k, v in P["seg_index"].items()}

# ---------- 校閱 chunk maps ----------
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
            sm, tm = SRC.search(blk), TRA.search(blk)
            chunk_map.setdefault(k, {})[seg] = (sm.group(1).strip() if sm else "",
                                                tm.group(1).strip() if tm else "")
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

delta, invert, conf = {}, {}, {}
for (book, chunk), segs in chunk_map.items():
    ps = txt_paras(book, chunk)
    if not ps:
        continue
    joined, offs, cur = norm("".join(ps)), [], 0
    for p in ps:
        offs.append(cur); cur += len(norm(p))
    ds, inv = [], {}
    for seg, (s, _) in segs.items():
        ns = norm(s)
        if not ns:
            continue
        pos = joined.find(ns)
        if pos < 0:
            continue
        a = max(i for i, o in enumerate(offs) if o <= pos)
        inv.setdefault(a, []).append(seg)
        ds.append(a - seg)
    invert[(book, chunk)] = inv
    if ds:
        c = Counter(ds)
        delta[(book, chunk)] = c.most_common(1)[0][0]
        conf[(book, chunk)] = c.most_common(1)[0][1] / len(ds)

CHUNK = re.compile(r"([0-9]{2}[a-z]|00_卷首)[_\u4e00-\u9fff]{0,8}\s*(?:#|＃)\s*(\d+)")
SECTION_CHUNK = re.compile(r"([0-9]{2}[a-z]|00_卷首)")
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
    out = []
    for t in ts:
        t = t.strip()
        if len(t) >= 2 and t not in out:
            out.append(t)
    out2 = []
    for t in out:
        k = nkey(t)[:24]
        if len(k) >= 2 and k not in out2:
            out2.append(k)
    return out2[:4]

def pick_tra(book, chunk, para, terms):
    """Choose the out paragraph index for a located TXT paragraph."""
    ops = out_paras(book, chunk)
    if not ops:
        return None, "", 0.0
    cm = chunk_map.get((book, chunk), {})
    inv = invert.get((book, chunk), {})
    d = delta.get((book, chunk))
    inv_para = [s for s in inv.get(para, []) if 1 <= s <= len(ops)]
    if inv_para:
        # segs whose 底本文字 is exactly this 分卷 paragraph: hard constraint
        hit = None
        for tl in sorted({len(t) for t in terms}, reverse=True):
            for s in inv_para:
                kj = cm.get(s)
                if kj and kj[0] and any(t in nkey(kj[0]) for t in terms if len(t) == tl):
                    hit = s
                    break
            if hit:
                break
        cands = ([hit] if hit else []) + inv_para
    else:
        cands = []
        if d is not None:
            cands = [para - d] + [para - d + k for k in (1, -1, 2, -2)]
    best, bsim = None, -1.0
    for s in dict.fromkeys(x for x in cands if x and 1 <= x <= len(ops)):
        kj = cm.get(s)
        sc = sim(ops[s - 1], kj[1]) if kj and kj[1] else 0.5
        if s == cands[0]:
            sc += 0.001
        if sc > bsim:
            best, bsim = s, sc
    return best, (ops[best - 1] if best else ""), bsim

resolved, unresolved = [], []
stats = Counter()
seen = {}

def clean_note(txt):
    t = txt.replace("**", "")
    t = re.sub(r"\s*\n\s*", " ", t)
    t = re.sub(r"\s{2,}", " ", t)
    return t.strip()

_kjc = {}
def kj_src(key):
    if key in _kjc:
        return _kjc[key]
    num = key.split("-")[0]
    p = os.path.join(ROOT, "校閱_10K", f"校閱_{num}.txt")
    _kjc[key] = ""
    if os.path.exists(p):
        t = rd(p)
        i = t.find(f"【{key}】")
        if i >= 0:
            seg = t[i:]
            m = re.search(r"\n【\d{3,4}-\d{4}】", seg[10:])
            end = (m.start() + 10) if m else len(seg)
            sm = SRC.search(seg[:end])
            if sm:
                _kjc[key] = sm.group(1).strip()
    return _kjc[key]

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
    cand = None
    ids = [k for k in (it.get("ids") or []) if k in P["seg_index"]]
    for key in (ids if terms else []):
        v = P["seg_index"][key]
        s_kj = kj_src(key)
        if not s_kj or not any(t in nkey(s_kj) for t in terms):
            continue
        ps = txt_paras(v["book"], v["chunk"])
        if not ps:
            continue
        joined, offs, cur = norm("".join(ps)), [], 0
        for p in ps:
            offs.append(cur); cur += len(norm(p))
        pos = joined.find(norm(s_kj))
        if pos < 0:
            continue
        para = max(i for i, o in enumerate(offs) if o <= pos)
        best, tra, bsim = pick_tra(v["book"], v["chunk"], para, terms)
        cand = (v["book"], v["chunk"], para, key, tra, bsim, "seg-verified")
        stats["seg-verified"] += 1
        break

    if not cand:
        m = CHUNK.search(it["raw"]) or CHUNK.search(it["body"])
        hint_chunk = ALIAS.get((bk, m.group(1))) if m else None
        if not hint_chunk:
            s = SECTION_CHUNK.search(it.get("section") or "")
            if s:
                hint_chunk = ALIAS.get((bk, s.group(1)))

        def scan(chunk):
            ps = txt_paras(bk, chunk)
            if not ps:
                return []
            res = []
            for i, txt in enumerate(ps):
                kt = nkey(txt)
                hits = [t for t in terms if t in kt]
                if hits:
                    res.append((i, max(len(t) for t in hits), len(hits)))
            return res

        bestloc = None
        for ch in ([hint_chunk] if hint_chunk else []):
            for i, tlen, nhit in scan(ch):
                sc = (tlen, nhit)
                if bestloc is None or sc > bestloc[0]:
                    bestloc = (sc, ch, i)
        if bestloc and not (bestloc[0][0] >= 4 or bestloc[0][1] >= 2):
            bestloc = None
        how = "chunk"
        if not bestloc:
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
                    bestloc = (allr[0][0], allr[0][1], allr[0][2])
                    how = "book"
                    if len(allr) > 1 and allr[0][0] == allr[1][0]:
                        stats["book-tie"] += 1
        if bestloc:
            sc, ch, i = bestloc
            bse, tra, bsim = pick_tra(bk, ch, i, terms)
            cand = (bk, ch, i, None, tra, bsim, how)
            stats[how] += 1

        # 3) 段號 fallback: trust 校閱's chunk#seg, but only if the chunk agrees
        #    with the chunk that the original record itself points at
        if not cand and ids and hint_chunk:
            pre = hint_chunk.split("_")[0]
            for key in ids:
                v = P["seg_index"][key]
                if not v["chunk"].startswith(pre):
                    continue
                s_kj = kj_src(key)
                ps = txt_paras(v["book"], v["chunk"])
                if not s_kj or not ps:
                    continue
                joined, offs, cur = norm("".join(ps)), [], 0
                for p in ps:
                    offs.append(cur); cur += len(norm(p))
                pos = joined.find(norm(s_kj))
                if pos < 0:
                    continue
                para = max(i for i, o in enumerate(offs) if o <= pos)
                bse, tra, bsim = pick_tra(v["book"], v["chunk"], para, terms)
                cand = (v["book"], v["chunk"], para, key, tra, bsim, "seg-hint")
                stats["seg-hint"] += 1
                break

        # 4) last resort: the record's own chunk#seg -> 校閱 seg numbering
        if not cand and hint_chunk:
            sg = None
            chg = CHUNK.search(it["raw"]) or CHUNK.search(it["body"])
            if chg:
                sg = int(chg.group(2))
            else:
                sh2 = re.search(r"#\s*(\d+)", it["raw"])
                if sh2:
                    sg = int(sh2.group(1))
            if sg:
                k2 = loc_index.get((bk, hint_chunk, sg))
                if k2:
                    s_kj = kj_src(k2)
                    ps = txt_paras(bk, hint_chunk)
                    if s_kj and ps:
                        joined, offs, cur = norm("".join(ps)), [], 0
                        for p in ps:
                            offs.append(cur); cur += len(norm(p))
                        pos = joined.find(norm(s_kj))
                        if pos >= 0:
                            para = max(i for i, o in enumerate(offs) if o <= pos)
                            bse, tra, bsim = pick_tra(bk, hint_chunk, para, terms)
                            cand = (bk, hint_chunk, para, k2, tra, bsim, "hint-seg")
                            stats["hint-seg"] += 1

    if not cand:
        unresolved.append({"raw": it["raw"], "body": it["body"], "src": it["src"],
                           "section": it.get("section", ""), "terms": terms[:2],
                           "files": it.get("files", []),
                           "reason": "無可檢索的引文" if not terms else "引文在原文中找不到"})
        continue

    b2, chunk, para, forced_label, tra, bsim, how = cand
    bk = b2
    ps = txt_paras(bk, chunk)
    src_txt = ps[para]
    ops = out_paras(bk, chunk)
    cm = chunk_map.get((bk, chunk), {})
    seg = None
    if forced_label and forced_label in P["seg_index"]:
        seg = P["seg_index"][forced_label]["seg"]
        tra = ops[seg - 1] if 1 <= seg <= len(ops) else ""
        kj = cm.get(seg)
        if kj and kj[1] and sim(tra, kj[1]) < 0.3:
            stats["re-pick"] += 1
            seg, tra, bsim = pick_tra(bk, chunk, para, terms)
    else:
        seg, tra, bsim = pick_tra(bk, chunk, para, terms)
    if not seg or not (1 <= seg <= len(ops)):
        stats["no-seg"] += 1
        unresolved.append({"raw": it["raw"], "body": it["body"], "src": it["src"],
                           "section": it.get("section", ""), "terms": terms[:2],
                           "files": it.get("files", []), "reason": "無法確定譯文段落"})
        continue
    # 原文: prefer the segment-sized 底本文字 recorded in 校閱 (verbatim slice of 分卷),
    # otherwise the whole 分卷 paragraph
    src = src_txt
    kjrec = cm.get(seg)
    if kjrec and kjrec[0].strip() and norm(kjrec[0]) in norm(src_txt):
        src = kjrec[0]
        stats["src-kj"] += 1
    else:
        stats["src-txt"] += 1
    if not tra:
        stats["no-tra"] += 1
        unresolved.append({"raw": it["raw"], "body": it["body"], "src": it["src"],
                           "section": it.get("section", ""), "terms": terms[:2],
                           "files": it.get("files", []), "reason": "無對應譯文"})
        continue
    if len(src) < 8 or len(tra) < 15:
        stats["too-short"] += 1
        unresolved.append({"raw": it["raw"], "body": it["body"], "src": it["src"],
                           "section": it.get("section", ""), "terms": terms[:2],
                           "files": it.get("files", []), "reason": "原文或譯文過短，疑定位不確"})
        continue
    if kjrec and kjrec[1] and sim(tra, kjrec[1]) < 0.3:
        stats["tra-mismatch"] += 1
        unresolved.append({"raw": it["raw"], "body": it["body"], "src": it["src"],
                           "section": it.get("section", ""), "terms": terms[:2],
                           "files": it.get("files", []), "reason": "原文與現行譯文段序對不上，不敢硬配"})
        continue
    label = ids[0] if ids else None
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
           "notes": [{"raw": it["raw"], "body": it["body"], "src": it["src"]}],
           "bsim": round(bsim, 2)}
    seen[label] = rec
    resolved.append(rec)
    stats["ok"] += 1

# merge same (book,chunk,seg) duplicates
by_loc = {}
final = []
for r in resolved:
    k = (r["book"], r["chunk"], r["seg"])
    if k in by_loc:
        t = by_loc[k]
        for s in r["srcs"]:
            if s not in t["srcs"]:
                t["srcs"].append(s)
        t["notes"] += r["notes"]
        stats["merged-loc"] += 1
        continue
    by_loc[k] = r
    final.append(r)
resolved = final

print("resolved", len(resolved), "unresolved", len(unresolved))
print(dict(stats))
print("books", Counter(r["book"] for r in resolved))
print("how", Counter(r["how"] for r in resolved))
json.dump({"resolved": resolved, "unresolved": unresolved},
          open(os.path.join(TOOLS, "n4_built.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
