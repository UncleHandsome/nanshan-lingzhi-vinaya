# -*- coding: utf-8 -*-
"""套用零頭批 7K 修改。
用法:
  python _7k_ling_apply.py check   # 只檢查 find 是否唯一並印出前後文
  python _7k_ling_apply.py apply   # 備份後寫回（保持行尾）
"""
import os, sys, io, json, shutil, re

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
X7 = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out")
BAK = os.path.join(ROOT, "歸檔", "7K卷修正前")
WORK = os.path.join(ROOT, "AI語譯", "_work", "review")

IDS = ["2536", "2537", "2629", "2804", "2805", "2806", "2807", "2808"]
_cache = {}


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def parse_x7(nnn):
    p = os.path.join(X7, "校閱_%s.txt" % nnn)
    lines = rd(p).replace("\r\n", "\n").split("\n")
    segs, cur = [], None
    for ln in lines:
        m = re.match(r"^【(\d{3,4}-\d{4})】\s*(\S+)#(\d+)\s*$", ln.strip())
        if m:
            cur = {"no": m.group(1), "chunk": m.group(2), "idx": int(m.group(3))}
            segs.append(cur)
            continue
    return segs


def read_chunk(chunk):
    if chunk in _cache:
        return _cache[chunk]
    book, name = chunk.split("/", 1)
    p = os.path.join(OUT, book, name + ".txt")
    raw = rd(p)
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    idxs = [i for i, l in enumerate(lines) if l.strip()]
    _cache[chunk] = (raw, eol, lines, idxs, p)
    return _cache[chunk]


def build_map():
    m = {}
    for n in IDS:
        for s in parse_x7(n):
            key = s["chunk"].split("/")[1].split("_")[0]
            m[key] = s["chunk"]
    return m


def main(mode):
    edits = json.loads(rd(os.path.join(WORK, "_7k_ling_edits.json")))
    cmap = build_map()
    touched = {}
    for key in sorted(edits):
        ck, idx = key.split("|")
        chunk = cmap[ck]
        raw, eol, lines, idxs, p = read_chunk(chunk)
        i = idxs[int(idx) - 1]
        old = lines[i]
        cur = old
        for op in edits[key]:
            f, n = op["find"], op["new"]
            c = cur.count(f)
            if c != 1:
                raise SystemExit("FIND 不唯一/不存在: %s count=%d %r" % (key, c, f))
            cur = cur.replace(f, n)
        if cur == old:
            raise SystemExit("無變化: %s" % key)
        print("--- %s" % key)
        print("[OLD] " + old)
        print("[NEW] " + cur)
        touched.setdefault(chunk, {})[int(idx)] = cur

    if mode != "apply":
        print("\n( check only: %d 段 / %d 檔 )" % (sum(len(v) for v in touched.values()), len(touched)))
        return

    for chunk, segmap in touched.items():
        raw, eol, lines, idxs, p = read_chunk(chunk)
        for idx, new in segmap.items():
            lines[idxs[idx - 1]] = new
        book, name = chunk.split("/", 1)
        d = os.path.join(BAK, book)
        if not os.path.isdir(d):
            os.makedirs(d)
        bp = os.path.join(d, name + "_v.txt")
        if not os.path.exists(bp):
            shutil.copy2(p, bp)
            print("備份 %s" % os.path.relpath(bp, ROOT))
        with io.open(p, "w", encoding="utf-8", newline="") as f:
            f.write(eol.join(lines))
        print("寫入 %s：%d 段" % (chunk, len(segmap)))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "check")
