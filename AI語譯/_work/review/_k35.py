# -*- coding: utf-8 -*-
"""7K 03_業疏 卷三之五a 校閱工具。
用法:
  python _k35.py sheets 2630-2654     # 產生 _k35_view/sheet_NNN.txt
  python _k35.py view 2630            # 印出單檔 sheet
  python _k35.py apply edits_2630.json   # {"n":2630,"edits":[{"idx":5,"ops":[{"find":..,"new":..}]}]}
  python _k35.py dump 2630 5 7        # 印指定段（原文/現行）
"""
import os, io, re, sys, json, shutil

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
X7 = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out")
RESP = os.path.join(ROOT, "batch_qwen", "r7k")
VIEW = os.path.join(ROOT, "AI語譯", "_work", "review", "_k35_view")
BAK = os.path.join(ROOT, "歸檔", "7K卷修正前")


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def parse(n):
    t = rd(os.path.join(X7, "校閱_%d.txt" % n)).replace("\r\n", "\n")
    segs, cur = [], None
    for ln in t.split("\n"):
        m = re.match(r"^【(\d{4}-\d{4})】\s*(\S+)#(\d+)\s*$", ln.strip())
        if m:
            cur = {"no": m.group(1), "chunk": m.group(2), "idx": int(m.group(3)), "src": "", "tr": ""}
            segs.append(cur); continue
        if cur is not None:
            if ln.startswith("【原文】"): cur["src"] = ln[4:].strip()
            elif ln.startswith("【譯文】"): cur["tr"] = ln[4:].strip()
    return segs


def sheet(n):
    if not os.path.isdir(VIEW):
        os.makedirs(VIEW)
    segs = parse(n)
    rp = os.path.join(RESP, "resp_%d.txt" % n)
    buf = ["#" * 8 + " resp_%d " % n + "#" * 8, ""]
    buf.append(rd(rp).strip() if os.path.exists(rp) else "(缺意見檔)")
    buf.append("")
    buf.append("#" * 8 + " 段落 %d " % n + "#" * 8)
    for s in segs:
        buf.append("")
        buf.append("=== %s  %s#%d ===" % (s["no"], s["chunk"], s["idx"]))
        buf.append("[原文] " + s["src"])
        buf.append("[現譯] " + s["tr"])
    out = os.path.join(VIEW, "sheet_%d.txt" % n)
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(buf) + "\n")
    return out


def chunk_lines(chunk):
    p = os.path.join(OUT, *chunk.split("/")) + ".txt"
    raw = rd(p)
    eol = "\r\n" if "\r\n" in raw else "\n"
    L = raw.split(eol)
    return p, raw, eol, L, [i for i, l in enumerate(L) if l.strip()]


def apply(efile):
    spec = json.loads(rd(efile))
    items = spec["items"] if "items" in spec else [spec]
    by_chunk = {}
    for it in items:
        n = it["n"]
        segs = {s["idx"]: s for s in parse(n)}
        for e in it["edits"]:
            s = segs[e["idx"]]
            by_chunk.setdefault(s["chunk"], []).append((s, e))
    total = 0
    for chunk, items in by_chunk.items():
        p, raw, eol, L, idxs = chunk_lines(chunk)
        for s, e in items:
            i = idxs[s["idx"] - 1]
            old = L[i]
            cur = old
            for op in e["ops"]:
                find, new = op["find"], op["new"]
                c = cur.count(find)
                if c != 1:
                    raise SystemExit("FIND 不唯一/不存在 %s #%d count=%d: %r" % (s["no"], s["idx"], c, find))
                cur = cur.replace(find, new)
            if cur == old:
                raise SystemExit("無變化 %s #%d" % (s["no"], s["idx"]))
            L[i] = cur
            total += 1
        book, name = chunk.split("/", 1)
        d = os.path.join(BAK, book)
        if not os.path.isdir(d):
            os.makedirs(d)
        bp = os.path.join(d, name + "_v.txt")
        if not os.path.exists(bp):
            shutil.copy2(p, bp)
            print("備份 " + os.path.relpath(bp, ROOT))
        with io.open(p, "w", encoding="utf-8", newline="") as f:
            f.write(eol.join(L))
        print("寫入 %s：%d 段" % (chunk, len(items)))
    print("合計 %d 段" % total)


def dump(n, want):
    segs = {s["idx"]: s for s in parse(n)}
    cache = {}
    for w in want:
        s = segs.get(str(w).zfill(4))
        if not s:
            print("(無此段 %s)" % w); continue
        if s["chunk"] not in cache:
            cache[s["chunk"]] = chunk_lines(s["chunk"])
        p, raw, eol, L, idxs = cache[s["chunk"]]
        print("\n=== %s %s#%d ===" % (s["no"], s["chunk"], s["idx"]))
        print("[原文] " + s["src"])
        print("[現譯] " + L[idxs[s["idx"] - 1]].strip())


def verify(efile):
    spec = json.loads(rd(efile))
    items = spec["items"] if "items" in spec else [spec]
    for it in items:
        n = it["n"]
        segs = {s["idx"]: s for s in parse(n)}
        cache = {}
        for e in it["edits"]:
            s = segs[e["idx"]]
            if s["chunk"] not in cache:
                cache[s["chunk"]] = chunk_lines(s["chunk"])
            p, raw, eol, L, idxs = cache[s["chunk"]]
            print("\n=== %s %s#%d 改後 ===" % (s["no"], s["chunk"], s["idx"]))
            print(L[idxs[s["idx"] - 1]].strip())


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "sheets":
        a, b = sys.argv[2].split("-")
        for n in range(int(a), int(b) + 1):
            print(sheet(n))
    elif cmd == "view":
        print(sheet(int(sys.argv[2])))
    elif cmd == "apply":
        apply(sys.argv[2])
    elif cmd == "verify":
        verify(sys.argv[2])
    elif cmd == "dump":
        dump(int(sys.argv[2]), sys.argv[3:])
