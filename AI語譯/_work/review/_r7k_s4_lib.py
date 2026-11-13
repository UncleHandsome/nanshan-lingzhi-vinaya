# -*- coding: utf-8 -*-
"""資持記 上四a 7K 校閱工具：讀校閱材料、比對現行譯文、套用修改。"""
import os, re, io, json, shutil, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT, "AI語譯", "out")
MAT = os.path.join(ROOT, "校閱_7K")
BAK = os.path.join(ROOT, "歸檔", "7K卷修正前")

HDR = re.compile(r"^【(\d{4})-(\d{4})】([^/]+)/(\d\d\w_[^#]+)#(\d+)\s*$")


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def load_mat(n):
    """回傳 [{'no','chunk','para','src','tr'}]"""
    p = os.path.join(MAT, "校閱_%d.txt" % n)
    txt = rd(p)
    lines = txt.split("\n")
    segs = []
    cur = None
    for ln in lines:
        m = HDR.match(ln.strip())
        if m:
            if cur:
                segs.append(cur)
            cur = {"no": m.group(1) + "-" + m.group(2), "book": m.group(3),
                   "chunk": m.group(4), "para": int(m.group(5)), "src": "", "tr": ""}
            continue
        if cur is None:
            continue
        s = ln.strip()
        if s.startswith("【原文】"):
            cur["src"] = s[4:]
        elif s.startswith("【譯文】"):
            cur["tr"] = s[4:]
    if cur:
        segs.append(cur)
    return segs


def load_out(chunk):
    """回傳 (raw, eol, lines, idxs)"""
    p = os.path.join(OUT, "資持記", chunk + ".txt")
    raw = rd(p)
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    idxs = [i for i, l in enumerate(lines) if l.strip()]
    return raw, eol, lines, idxs


def check(nums):
    bad = 0
    for n in nums:
        for s in load_mat(n):
            _, _, lines, idxs = load_out(s["chunk"])
            cur = lines[idxs[s["para"] - 1]]
            if cur != s["tr"]:
                bad += 1
                print("DIFF %s %s#%d" % (s["no"], s["chunk"], s["para"]))
                print("  OUT: %s" % cur[:120])
                print("  MAT: %s" % s["tr"][:120])
    print("checked, diff=%d" % bad)


def apply(edits, dry=False):
    total = 0
    for chunk, segs in edits.items():
        p = os.path.join(OUT, "資持記", chunk + ".txt")
        raw, eol, lines, idxs = load_out(chunk)
        for no, e in segs.items():
            idx = e["idx"]
            i = idxs[idx - 1]
            old = lines[i]
            cur = old
            for find, new in e["ops"]:
                c = cur.count(find)
                if c != 1:
                    raise SystemExit("FIND 不唯一/不存在: %s #%d count=%d %r" % (no, idx, c, find))
                cur = cur.replace(find, new)
            if cur == old:
                raise SystemExit("無變化: %s #%d" % (no, idx))
            lines[i] = cur
            total += 1
        if not dry:
            d = os.path.join(BAK, "資持記")
            if not os.path.isdir(d):
                os.makedirs(d)
            bp = os.path.join(d, chunk + "_v.txt")
            if not os.path.exists(bp):
                shutil.copy2(p, bp)
                print("備份 %s" % os.path.relpath(bp, ROOT))
            with io.open(p, "w", encoding="utf-8", newline="") as f:
                f.write(eol.join(lines))
        print("寫入 %s：%d 段" % (chunk, len(segs)))
    print("合計 %d 段" % total)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "check":
        check([int(x) for x in sys.argv[2:]])
    elif cmd == "show":
        for n in [int(x) for x in sys.argv[2:]]:
            for s in load_mat(n):
                print("== %s %s#%d" % (s["no"], s["chunk"], s["para"]))
                print("原：" + s["src"])
                print("譯：" + s["tr"])
    elif cmd == "apply":
        for f in sys.argv[2:]:
            apply(json.loads(rd(f)))
