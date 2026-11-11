# -*- coding: utf-8 -*-
"""Per-chunk triage digest for r2 02_戒疏 pass 2.

For a chunk token (e.g. "13a"), locate Qwen claim blocks to segments via:
  1. 【NNN-MMMM】 material id (own prefix, same chunk)
  2. #NN fallback
  3. unique long quote (「...」/『...』) found in exactly one current paragraph
Then rank live claims (quote matches current text first) and emit a digest.
"""
import io, os, re, json, sys, collections

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
HERE = os.path.join(ROOT, "AI語譯", "_work", "review", "_r2_02")
OUTD = os.path.join(ROOT, "AI語譯", "out", "02_戒疏")
R2 = os.path.join(ROOT, "batch_qwen", "r2")
PER = json.load(io.open(os.path.join(HERE, "tmp_per.json"), encoding="utf-8"))

STRONG = re.compile(r"相反|顛倒|譯反|譯成|主詞|主語|受詞|施受|應作|當作|誤譯|譯錯|讀成|當成|混為|矛盾|不成詞|非是|錯解|誤解|說反|失準|曲解|失義|誤作|脫文|脫落|讀為|解為|訓為|猶|即是|漏|增")
QUOTE = re.compile(r"[「『]([^」』\n]{6,80})[」』]")


def fullname(tok):
    names = set()
    for k in PER:
        for v in PER[k].values():
            nm = v[0].split("/")[1]
            if nm.split("_")[0] == tok:
                names.add(nm)
    assert len(names) == 1, (tok, names)
    return names.pop()


def paras(chunk):
    t = io.open(os.path.join(OUTD, chunk + ".txt"), encoding="utf-8", newline="").read()
    ps = t.split("\r\n\r\n")
    if ps and ps[-1].endswith("\r\n"):
        ps[-1] = ps[-1][:-2]
    return ps


def build(tok, topn=5, cl=195, pl=195, path=None, verbose=False):
    chunk = fullname(tok)
    files = sorted(int(k) for k in PER if any(v[0].split("/")[1] == chunk for v in PER[k].values()))
    ps = paras(chunk)
    claims = []          # (match, score, n, segs, block)
    unlocated = []
    for n in files:
        d = PER[str(n)]
        segs_of = {v[1] for v in d.values() if v[0].split("/")[1] == chunk}
        t = io.open(os.path.join(R2, "resp_%d.txt" % n), encoding="utf-8-sig", errors="replace").read()
        blocks = [b.strip() for b in re.split(r"\n\s*\n", t) if b.strip()]
        for b in blocks:
            segs = []
            for mm in re.finditer(r"(\d{3})-(\d{4})", b):
                k = mm.group(1) + "-" + mm.group(2)
                if k in d and d[k][0].split("/")[1] == chunk:
                    segs.append(d[k][1])
            if not segs:
                for mm in re.finditer(r"【(\d{4})】", b):
                    k = str(n) + "-" + mm.group(1)
                    if k in d and d[k][0].split("/")[1] == chunk:
                        segs.append(d[k][1])
            if not segs:
                for mm in re.finditer(r"(?<![\d-])(\d{4})(?![\d-])", b):
                    k = str(n) + "-" + mm.group(1)
                    if k in d and d[k][0].split("/")[1] == chunk:
                        segs.append(d[k][1])
            if not segs:
                for mm in re.finditer(r"(?<!\d)#?(\d{1,3})(?!\d)", b):
                    s = int(mm.group(1))
                    if s in segs_of:
                        segs.append(s)
            quotes = QUOTE.findall(b)
            if not segs and quotes:
                for q in quotes:
                    hit = [i + 1 for i, p in enumerate(ps) if q in p]
                    if len(hit) == 1:
                        segs.append(hit[0])
                        break
            sc = len(STRONG.findall(b))
            if sc == 0:
                continue
            if not segs:
                unlocated.append((sc, n, b))
                continue
            match = 0
            for s in set(segs):
                if 0 < s <= len(ps) and any(q in ps[s - 1] for q in quotes):
                    match = 1
                    break
            claims.append((match, sc, n, sorted(set(segs)), b))

    # dedupe identical block text, merging segs
    merged = collections.OrderedDict()
    for m, sc, n, segs, b in claims:
        key = (n, re.sub(r"\s+", "", b)[:120])
        if key in merged:
            old = merged[key]
            merged[key] = (max(old[0], m), max(old[1], sc), n, sorted(set(old[3]) | set(segs)), b)
        else:
            merged[key] = (m, sc, n, segs, b)
    ranked = sorted(merged.values(), key=lambda x: (-x[0], -x[1], x[3][0]))

    L = []
    L.append("#### %s segs=%d files=%d claims=%d unlocated=%d" % (tok, len(ps), len(files), len(ranked), len(unlocated)))
    for m, sc, n, segs, b in ranked[:topn]:
        L.append("=== resp_%d %s score=%d [%s]" % (n, ",".join("#%d" % s for s in segs), sc, "LIVE" if m else "quote?"))
        L.append("CLAIM: " + b.replace("\n", " / ")[:cl])
        s = segs[0]
        L.append("NOW  : " + (ps[s - 1][:pl] if 0 < s <= len(ps) else "NA"))
        L.append("")
    rest = ranked[topn:]
    if rest:
        L.append("REST: " + " | ".join("resp_%d %s(%d)" % (n, ",".join("#%d" % s for s in segs), sc) for m, sc, n, segs, b in rest))
    if unlocated:
        L.append("UNLOC(%d): " % len(unlocated) + " || ".join("#%d:%s" % (n, re.sub(r"\s+", " ", b)[:80]) for sc, n, b in unlocated[:3]))
    p = path or os.path.join(HERE, "dg_" + tok + ".txt")
    body = "\n".join(L)
    io.open(p, "w", encoding="utf-8").write(body)
    return p, len(body), len(ranked), len(unlocated)


if __name__ == "__main__":
    tok = sys.argv[1]
    topn = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    print(build(tok, topn=topn))
