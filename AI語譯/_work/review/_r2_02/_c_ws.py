# -*- coding: utf-8 -*-
"""Build per-chunk worksheet: claim full text + current paragraph + material 原文."""
import io, os, re, sys, json

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
HERE = os.path.join(ROOT, "AI語譯", "_work", "review", "_r2_02")
OUTD = os.path.join(ROOT, "AI語譯", "out", "02_戒疏")
J10 = os.path.join(ROOT, "校閱_10K")

# ---- material index: id -> (chunk, seg, src, oldtr) ----
MAT = {}
seg2id = {}
def load_mat(n):
    p = os.path.join(J10, "校閱_%03d.txt" % n)
    if not os.path.exists(p):
        return
    t = io.open(p, encoding="utf-8-sig", errors="replace").read()
    for blk in re.split(r"(?=【\d{3}-\d{4}】)", t):
        m = re.match(r"【(\d{3})-(\d{4})】\s*([^\s#]+)#(\d+)\s*\n(.*)", blk, re.S)
        if not m:
            continue
        key = m.group(1) + "-" + m.group(2)
        chunk = m.group(3).split("/")[-1]
        seg = int(m.group(4))
        body = m.group(5)
        src = old = ""
        ms = re.search(r"【原文】(.*?)(?=\n【譯文】|\Z)", body, re.S)
        mt = re.search(r"【譯文】(.*?)(?=\n【|\Z)", body, re.S)
        if ms: src = ms.group(1).strip()
        if mt: old = mt.group(1).strip()
        MAT[key] = (chunk, seg, src, old)
        seg2id.setdefault((chunk, seg), key)

def paras(chunk):
    t = io.open(os.path.join(OUTD, chunk + ".txt"), encoding="utf-8", newline="").read()
    ps = t.split("\r\n\r\n")
    if ps and ps[-1].endswith("\r\n"):
        ps[-1] = ps[-1][:-2]
    return ps

def clean(t):
    t = t.replace("**", "").replace("###", "")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{2,}", "\n", t)
    return t.strip()

def main(tok):
    E = json.load(io.open(os.path.join(HERE, "_c_work.json"), encoding="utf-8"))
    sel = [e for e in E if e["tok"] == tok]
    if not sel:
        print("none"); return
    chunk = sel[0]["chunk"]
    for e in sel:
        for k in list(MAT):
            pass
    ps = paras(chunk)
    L = ["#### %s  claims=%d segs=%d paras=%d" % (chunk, len(sel),
         len({s for e in sel for s in e["segs"]}), len(ps)), ""]
    for i, e in enumerate(sel, 1):
        L.append("[%d] resp_%d %s score=%d %s" % (
            i, e["resp"], ",".join("#%d" % s for s in e["segs"]), e["score"],
            "LIVE" if e["live"] else "quote?"))
        s0 = e["segs"][0]
        for s in e["segs"]:
            k = seg2id.get((chunk, s))
            if k:
                L.append("SEG %d SRC(%s): %s" % (s, k, MAT[k][2][:240]))
            else:
                L.append("SEG %d SRC: (none)" % s)
            L.append("SEG %d NOW: %s" % (s, ps[s-1] if 0 < s <= len(ps) else "NA"))
            if k and MAT[k][3] and MAT[k][3] != (ps[s-1] if 0 < s <= len(ps) else ""):
                L.append("SEG %d OLD: %s" % (s, MAT[k][3]))
        L.append("CLAIM: " + clean(e["text"]))
        L.append("")
    body = "\n".join(L)
    p = os.path.join(HERE, "_c_ws_%s.txt" % tok)
    io.open(p, "w", encoding="utf-8").write(body)
    print(p, len(body))

if __name__ == "__main__":
    # build material index for all needed numbers
    E = json.load(io.open(os.path.join(HERE, "_c_work.json"), encoding="utf-8"))
    for n in sorted({e["resp"] for e in E}):
        load_mat(n)
    print("mat ids", len(MAT))
    args = sys.argv[1:]
    if args:
        for a in args: main(a)
    else:
        tot = 0
        for tok in sorted({e["tok"] for e in E}):
            main(tok)
