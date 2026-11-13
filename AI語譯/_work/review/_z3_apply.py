# -*- coding: utf-8 -*-
"""卷下之三 7K 套改器。
用法: python _z3_apply.py <chunk> <edits.json> [--dry]
edits.json: {"359-0001": {"idx": 3, "ops": [["find","new"], ...]}, ...}
idx 可省略，會由校閱檔段號反查；同一段可多次給 ops，依序套用。
"""
import os, sys, re, json, shutil, io

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
X7 = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out")
BAK = os.path.join(ROOT, "歸檔", "7K卷修正前")


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def parse_x7(n):
    p = os.path.join(X7, "校閱_%s.txt" % n)
    t = rd(p).replace("\r\n", "\n")
    segs, cur = [], None
    for ln in t.split("\n"):
        m = re.match(r"^【(\d{3,4}-\d{4})】\s*(\S+)#(\d+)\s*$", ln.strip())
        if m:
            cur = {"no": m.group(1), "chunk": m.group(2), "idx": int(m.group(3))}
            segs.append(cur)
    return segs


def main():
    chunk = sys.argv[1]
    efile = sys.argv[2]
    dry = "--dry" in sys.argv
    edits = json.loads(rd(efile))
    book, name = chunk.split("/", 1)
    p = os.path.join(OUT, book, name + ".txt")
    raw = rd(p)
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    idxs = [i for i, l in enumerate(lines) if l.strip()]

    segmap = {}
    for n in range(359, 397):
        for s in parse_x7(n):
            if s["chunk"] == chunk:
                segmap[s["no"]] = s
    changed = 0
    for no in sorted(edits):
        e = edits[no]
        idx = e.get("idx") if isinstance(e, dict) and "idx" in e else segmap[no]["idx"]
        i = idxs[idx - 1]
        old = lines[i]
        cur = old
        for find, new in e["ops"] if isinstance(e, dict) else e:
            c = cur.count(find)
            if c != 1:
                raise SystemExit("FIND 不唯一/不存在: %s #%d count=%d %r" % (no, idx, c, find))
            cur = cur.replace(find, new, 1)
        if cur == old:
            raise SystemExit("無變化: %s #%d" % (no, idx))
        lines[i] = cur
        changed += 1
    if dry:
        print("dry ok: %d 段可套用" % changed)
        return
    d = os.path.join(BAK, book)
    os.makedirs(d, exist_ok=True)
    bp = os.path.join(d, name + "_v.txt")
    if not os.path.exists(bp):
        shutil.copy2(p, bp)
        print("備份 %s" % os.path.relpath(bp, ROOT))
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(eol.join(lines))
    print("寫入 %s：%d 段" % (chunk, changed))


if __name__ == "__main__":
    main()
