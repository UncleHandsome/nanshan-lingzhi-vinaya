# -*- coding: utf-8 -*-
"""Apply r2 pass-2 edits, byte-preserving except the edited paragraph.

ops JSON: [{"chunk": "13a_卷三下之一", "seg": 46, "old": "...", "new": "...", "note": "..."}]
- backup: 歸檔/r2修正前/02_戒疏/<chunk>.txt  (created once, never overwritten)
- applies old->new inside paragraph[seg-1]; requires old unique in paragraph
- writes raw text back with CRLF preserved (utf-8, newline='')
"""
import io, os, sys, json, shutil

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
HERE = os.path.join(ROOT, "AI語譯", "_work", "review", "_r2_02")
OUTD = os.path.join(ROOT, "AI語譯", "out", "02_戒疏")
BAK = os.path.join(ROOT, "歸檔", "r2修正前", "02_戒疏")
LOG = os.path.join(HERE, "_apply2_log.jsonl")


def read_raw(chunk):
    return io.open(os.path.join(OUTD, chunk + ".txt"), encoding="utf-8", newline="").read()


def split_paras(raw):
    ps = raw.split("\r\n\r\n")
    tail = ""
    if ps and ps[-1].endswith("\r\n"):
        ps[-1] = ps[-1][:-2]
        tail = "\r\n"
    return ps, tail


def apply(ops_path):
    ops = json.load(io.open(ops_path, encoding="utf-8-sig"))
    by = {}
    for o in ops:
        by.setdefault(o["chunk"], []).append(o)
    results = []
    for chunk, olist in by.items():
        src = os.path.join(OUTD, chunk + ".txt")
        bak = os.path.join(BAK, chunk + ".txt")
        os.makedirs(BAK, exist_ok=True)
        if not os.path.exists(bak):
            shutil.copy2(src, bak)
        raw = read_raw(chunk)
        ps, tail = split_paras(raw)
        ok = 0
        for o in olist:
            i = o["seg"] - 1
            if not (0 <= i < len(ps)):
                results.append(("SKIP", chunk, o["seg"], "超出段數"))
                continue
            p = ps[i]
            n = p.count(o["old"])
            if n == 0:
                results.append(("MISS", chunk, o["seg"], o["old"][:40]))
                continue
            if n > 1:
                results.append(("DUP", chunk, o["seg"], o["old"][:40] + " x%d" % n))
                continue
            newp = p.replace(o["old"], o["new"])
            if newp == p:
                results.append(("NOOP", chunk, o["seg"], o["old"][:40]))
                continue
            # replace exactly this paragraph occurrence in raw
            if raw.count(p) != 1:
                results.append(("AMBIG", chunk, o["seg"], "段落字串不唯一"))
                continue
            raw = raw.replace(p, newp)
            ps[i] = newp
            ok += 1
            results.append(("OK", chunk, o["seg"], o["old"][:26] + " -> " + o["new"][:26]))
            io.open(LOG, "a", encoding="utf-8").write(json.dumps(
                {"chunk": chunk, "seg": o["seg"], "old": o["old"], "new": o["new"],
                 "note": o.get("note", "")}, ensure_ascii=False) + "\n")
        io.open(src, "w", encoding="utf-8", newline="").write(raw)
    # report
    lines = ["%s %s #%s %s" % r for r in results]
    bad = [r for r in results if r[0] != "OK"]
    io.open(os.path.join(HERE, "_apply2_out.txt"), "w", encoding="utf-8").write("\n".join(lines))
    print("applied", sum(1 for r in results if r[0] == "OK"), "of", len(results), "bad", len(bad))
    for r in bad:
        print(r)


if __name__ == "__main__":
    apply(sys.argv[1])
