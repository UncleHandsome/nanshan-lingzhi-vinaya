# -*- coding: utf-8 -*-
"""Build claim corpus for resp_550-876 with chunk/seg location."""
import io, os, re, json, collections

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
HERE = os.path.join(ROOT, "AI語譯", "_work", "review", "_rs")
R2 = os.path.join(ROOT, "batch_qwen", "r2")
OUTD = os.path.join(ROOT, "AI語譯", "out", "02_戒疏")
PER = json.load(io.open(os.path.join(ROOT, "AI語譯", "_work", "review", "_r2_02", "tmp_per.json"), encoding="utf-8"))

QUOTE = re.compile(r"[「『]([^」』\n]{6,90})[」』]")
CLAIM = re.compile(r"問題|建議|應作|宜作|宜改|改為|改作|誤|漏|增譯|脫|應是|不當|不符|矛盾|相反|顛倒|生硬|可作|不妥|欠|缺|錯|混|失|費解|難懂|不統一|不一致|歧義|贅|多餘|語病|搭配|不通|未譯|查無|無據|重複|累贅|簡化|順|白話|語氣")

def paras(chunk):
    t = io.open(os.path.join(OUTD, chunk + ".txt"), encoding="utf-8", newline="").read()
    ps = t.split("\r\n\r\n")
    if ps and ps[-1].endswith("\r\n"):
        ps[-1] = ps[-1][:-2]
    return ps

def chunk_names():
    d = {}
    for k, dd in PER.items():
        for mid, v in dd.items():
            nm = v[0].split("/")[1]
            d.setdefault(nm.split("_")[0], set()).add(nm)
    return {k: list(v)[0] for k, v in d.items() if len(v) == 1}

CH = chunk_names()
PSEG = {}

def get_paras(chunk):
    if chunk not in PSEG:
        PSEG[chunk] = paras(chunk)
    return PSEG[chunk]

# index of material ids per resp number
BYRESP = collections.defaultdict(dict)
for n, dd in PER.items():
    for mid, v in dd.items():
        BYRESP[int(n)][mid] = (v[0].split("/")[1], v[1])

# authoritative id map for 02_戒疏 (covers 550-641 as well)
MAP = json.load(io.open(os.path.join(ROOT, "AI語譯", "_work", "review", "_r2_02", "_map.json"), encoding="utf-8"))["idx"]
for mid, v in MAP.items():
    if v.get("book") != "02_戒疏":
        continue
    n = int(mid.split("-")[0])
    BYRESP.setdefault(n, {})[mid] = (v["chunk"], v["seg"])

def locate(n, b):
    d = BYRESP.get(n, {})
    segs = []
    chunks = set()
    for mm in re.finditer(r"(?<!\d)(\d{3})-(\d{4})(?!\d)", b):
        k = mm.group(1) + "-" + mm.group(2)
        if k in d:
            chunks.add(d[k][0]); segs.append(d[k][1])
    if not segs:
        for mm in re.finditer(r"【(\d{4})】", b):
            k = "%d-%s" % (n, mm.group(1))
            if k in d:
                chunks.add(d[k][0]); segs.append(d[k][1])
    if not segs:
        for mm in re.finditer(r"(?<![\d-])(\d{4})(?![\d-])", b):
            k = "%d-%s" % (n, mm.group(1))
            if k in d:
                chunks.add(d[k][0]); segs.append(d[k][1])
    return sorted(chunks), sorted(set(s for s in segs if s > 0))

files = sorted(int(f[5:-4]) for f in os.listdir(R2) if re.match(r"resp_\d+\.txt$", f) and 550 <= int(f[5:-4]) <= 876)
claims = []
for n in files:
    t = io.open(os.path.join(R2, "resp_%d.txt" % n), encoding="utf-8-sig", errors="replace").read()
    blocks = [x.strip() for x in re.split(r"\n\s*\n", t) if x.strip()]
    for bi, b in enumerate(blocks):
        if len(b) < 8: continue
        cs, segs = locate(n, b)
        claims.append({"rid": n, "bi": bi, "text": re.sub(r"\s+", " ", b),
                       "chunks": cs, "segs": segs,
                       "nclaim": bool(CLAIM.search(b)), "nchar": len(b)})

json.dump(claims, io.open(os.path.join(HERE, "claims.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("resp files", len(files), "blocks", len(claims))
print("located", sum(1 for c in claims if c["segs"]), "unlocated", sum(1 for c in claims if not c["segs"]))
print("claim-ish", sum(1 for c in claims if c["nclaim"]))
print("by chunk", sorted(collections.Counter(c["chunks"][0][:3] for c in claims if c["chunks"]).items()))
