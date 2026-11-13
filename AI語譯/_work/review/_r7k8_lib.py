# -*- coding: utf-8 -*-
"""04_比丘尼鈔 卷上之下a 7K 校閱：列行 / 套用。
用法:
  python _r7k8_lib.py line 02a 16 17 18        # 印出 chunk 非空行第 N 行（1-based）全文
  python _r7k8_lib.py cnt 02a 16               # 印出某行長度/片段
  python _r7k8_lib.py apply edits.json         # 套用 [{chunk,idx,find,new}, ...]，備份 _v.txt
"""
import os, sys, json, shutil, io

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT, "AI語譯", "out", "04_比丘尼鈔")
BAK = os.path.join(ROOT, "歸檔", "7K卷修正前", "04_比丘尼鈔")


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def load(name):
    p = os.path.join(OUT, name + ".txt")
    raw = rd(p)
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    idxs = [i for i, l in enumerate(lines) if l.strip()]
    return p, raw, eol, lines, idxs


def show(name, nums):
    p, raw, eol, lines, idxs = load(name)
    for n in nums:
        print("=== %s #%s ===" % (name, n))
        print(lines[idxs[int(n) - 1]])
        print()


def apply(efile):
    items = json.loads(rd(efile))
    cache = {}
    done = {}
    for it in items:
        name = it["chunk"]
        if name not in cache:
            cache[name] = load(name)
        p, raw, eol, lines, idxs = cache[name]
        i = idxs[int(it["idx"]) - 1]
        cur = lines[i]
        c = cur.count(it["find"])
        if c != 1:
            raise SystemExit("FIND 不唯一/不存在: %s #%s count=%d\n%r" % (name, it["idx"], c, it["find"]))
        lines[i] = cur.replace(it["find"], it["new"])
        done.setdefault(name, set()).add(it["idx"])
    for name, (p, raw, eol, lines, idxs) in cache.items():
        if not os.path.isdir(BAK):
            os.makedirs(BAK)
        bp = os.path.join(BAK, name + "_v.txt")
        if not os.path.exists(bp):
            shutil.copy2(p, bp)
            print("備份 %s" % bp)
        with io.open(p, "w", encoding="utf-8", newline="") as f:
            f.write(eol.join(lines))
        print("寫入 %s：段 %s" % (name, ",".join(sorted([str(x) for x in done[name]], key=int))))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "line":
        show(sys.argv[2], sys.argv[3:])
    elif cmd == "apply":
        apply(sys.argv[2])
