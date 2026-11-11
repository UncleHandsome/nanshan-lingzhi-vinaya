# -*- coding: utf-8 -*-
"""Build per-chunk worksheet: claim full text + current paragraph (deduped, no SRC)."""
import io, os, re, sys, json

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
HERE = os.path.join(ROOT, "AI語譯", "_work", "review", "_r2_02")
OUTD = os.path.join(ROOT, "AI語譯", "out", "02_戒疏")


def paras(chunk):
    t = io.open(os.path.join(OUTD, chunk + ".txt"), encoding="utf-8", newline="").read()
    ps = t.split("\r\n\r\n")
    if ps and ps[-1] == "":
        ps = ps[:-1]
    return ps


def clean(t):
    t = t.replace("**", "").replace("###", "")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{2,}", "\n", t)
    return t.strip()


def main(tok, cap=420):
    E = json.load(io.open(os.path.join(HERE, "_c_work.json"), encoding="utf-8"))
    sel = [e for e in E if e["tok"] == tok]
    if not sel:
        print("none"); return
    chunk = sel[0]["chunk"]
    ps = paras(chunk)
    L = ["#### %s  claims=%d segs=%d paras=%d" % (chunk, len(sel),
         len({s for e in sel for s in e["segs"]}), len(ps)), ""]
    seen = set()
    for i, e in enumerate(sel, 1):
        L.append("[%d] resp_%d %s s=%d %s" % (
            i, e["resp"], ",".join("#%d" % s for s in e["segs"]), e["score"],
            "LIVE" if e["live"] else "quote?"))
        L.append("CLAIM: " + clean(e["text"]))
        for s in e["segs"]:
            if s in seen:
                L.append("SEG %d NOW: (略，同前)" % s)
                continue
            seen.add(s)
            txt = ps[s - 1] if 0 < s <= len(ps) else "NA"
            L.append("SEG %d NOW: %s" % (s, txt[:cap] + ("…" if len(txt) > cap else "")))
        L.append("")
    body = "\n".join(L)
    p = os.path.join(HERE, "_c_ws_%s.txt" % tok)
    io.open(p, "w", encoding="utf-8").write(body)
    print(p, len(body))


if __name__ == "__main__":
    for a in sys.argv[1:]:
        main(a)
