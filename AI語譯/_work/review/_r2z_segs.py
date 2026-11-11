# -*- coding: utf-8 -*-
"""Extract 資持記 segments from 校閱_10K material; compare with current out paragraphs."""
import io, os, re, json, sys
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
MAT = os.path.join(ROOT, "校閱_10K")
OUTD = os.path.join(ROOT, "AI語譯", "out", "資持記")
WORK = os.path.join(ROOT, "AI語譯", "_work", "review")

pat = re.compile(r"^【(\d{3})-(\d{4})】\s*([^/\s]+)/([^#\s]+)#(\d+)\s*$")

def parse_material(n):
    p = os.path.join(MAT, "校閱_%03d.txt" % n)
    txt = io.open(p, encoding="utf-8").read()
    body = txt.split("# 材料開始", 1)[-1]
    segs = []
    cur = None
    for line in body.split("\n"):
        s = line.strip()
        m = pat.match(s)
        if m:
            cur = {"gid": "%s-%s" % (m.group(1), m.group(2)), "book": m.group(3),
                   "chunk": m.group(4), "seg": int(m.group(5)),
                   "src": "", "tr": ""}
            segs.append(cur)
            continue
        if cur is None:
            continue
        if s.startswith("【原文】"):
            cur["src"] += s[len("【原文】"):]
        elif s.startswith("【譯文】"):
            cur["tr"] += s[len("【譯文】"):]
        elif s and cur["tr"]:
            cur["tr"] += s
        elif s:
            cur["src"] += s
    return segs

def out_paras(chunk):
    p = os.path.join(OUTD, chunk + ".txt")
    txt = io.open(p, encoding="utf-8").read()
    return [l for l in txt.split("\n") if l.strip()]

def main():
    which = sys.argv[1:] or None
    allsegs = {}
    for n in range(876, 1000):
        for s in parse_material(n):
            if s["book"] != "資持記":
                continue
            s["n"] = n
            allsegs[s["gid"]] = s
    # coverage stats
    chunks = {}
    for s in allsegs.values():
        chunks.setdefault(s["chunk"], set()).add(s["seg"])
    print("segs:", len(allsegs), "chunks:", len(chunks))
    # compare material tr vs out paragraph
    diff = same = 0
    for s in allsegs.values():
        ps = out_paras(s["chunk"])
        if s["seg"] <= len(ps):
            if ps[s["seg"] - 1].strip() == s["tr"].strip():
                same += 1
            else:
                diff += 1
    print("material tr == out para:", same, " differ:", diff)
    json.dump({k: v for k, v in allsegs.items()},
              io.open(os.path.join(WORK, "_r2z_segs.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    # dump a specific material file
    if which:
        for a in which:
            n = int(a)
            segs = [s for s in allsegs.values() if s["n"] == n]
            ps = out_paras(segs[0]["chunk"]) if segs else []
            with io.open(os.path.join(WORK, "_r2z_dump_%03d.txt" % n), "w", encoding="utf-8") as f:
                for s in sorted(segs, key=lambda x: x["seg"]):
                    f.write("=== %s %s#%d  (@out para %d, out_len=%d, mat_len=%d, SAME=%s)\n" % (
                        s["gid"], s["chunk"], s["seg"], s["seg"],
                        len(ps[s["seg"]-1]) if s["seg"] <= len(ps) else -1,
                        len(s["tr"]),
                        ps[s["seg"]-1].strip() == s["tr"].strip() if s["seg"] <= len(ps) else "NA"))
                    f.write("【原文】%s\n" % s["src"])
                    f.write("【譯文-材料】%s\n" % s["tr"])
                    if s["seg"] <= len(ps):
                        f.write("【譯文-現行】%s\n" % ps[s["seg"]-1])
                    f.write("\n")
            print("dumped", n, len(segs))

main()
