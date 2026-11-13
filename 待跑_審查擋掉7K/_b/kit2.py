# -*- coding: utf-8 -*-
"""7K 後12（02_戒疏 B組）助手：讀材料 / 讀現行 / 比對 / 套用改動。
用法:
  python kit2.py dump NNN [NNN...]   # 產出 view_NNN.txt（材料＋現行＋差異）
  python kit2.py apply NNN           # 套用 _b/edits_NNN.json
"""
import os, sys, re, json, shutil, io, difflib

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
X7 = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out")
BAK = os.path.join(ROOT, "歸檔", "7K擋檔修正前")
HERE = os.path.dirname(os.path.abspath(__file__))

SEG_RE = re.compile(r"^【(\d{3,4})-(\d{4})】(02_戒疏)/([^#]+)#(\d+)\s*$")


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def parse7k(nnn):
    path = os.path.join(X7, "校閱_%s.txt" % nnn)
    segs = []
    cur = None
    for raw in rd(path).replace("\r\n", "\n").split("\n"):
        m = SEG_RE.match(raw.strip())
        if m:
            cur = {"no": "%s-%s" % (m.group(1), m.group(2)), "book": m.group(3),
                   "chunk": m.group(4), "idx": int(m.group(5)), "src": "", "tr": ""}
            segs.append(cur)
            continue
        if cur is not None:
            if raw.startswith("【原文】"):
                cur["src"] = raw[len("【原文】"):]
            elif raw.startswith("【譯文】"):
                cur["tr"] = raw[len("【譯文】"):]
    return segs


def read_chunk(chunk):
    p = os.path.join(OUT, "02_戒疏", chunk + ".txt")
    raw = rd(p)
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    idxs = [i for i, l in enumerate(lines) if l.strip()]
    return raw, eol, lines, idxs, p


def cur_text(seg):
    raw, eol, lines, idxs, p = read_chunk(seg["chunk"])
    return lines[idxs[seg["idx"] - 1]].strip()


def diffmark(a, b):
    sm = difflib.SequenceMatcher(None, a, b)
    ops = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "replace":
            ops.append("%r -> %r" % (a[i1:i2], b[j1:j2]))
        elif tag == "delete":
            ops.append("刪 %r" % (a[i1:i2],))
        elif tag == "insert":
            ops.append("增 %r" % (b[j1:j2],))
    return " ｜ ".join(ops) if ops else "(同)"


def dump(nnn):
    segs = parse7k(nnn)
    buf = []
    for s in segs:
        c = cur_text(s)
        same = (c == s["tr"])
        buf.append("=== %s  %s#%d  %s" % (s["no"], s["chunk"], s["idx"],
                                          "現行=材料" if same else "現行已異動"))
        buf.append("[原文] " + s["src"])
        buf.append("[材料] " + s["tr"])
        if not same:
            buf.append("[現行] " + c)
            buf.append("[差異] " + diffmark(s["tr"], c))
        buf.append("")
    out = os.path.join(HERE, "view_%s.txt" % nnn)
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(buf) + "\n")
    print("wrote view_%s.txt  (%d segs, %d 異動)" % (nnn, len(segs), sum(1 for s in segs if cur_text(s) != s["tr"])))


def apply_edits(nnn, edits):
    segs = {s["no"]: s for s in parse7k(nnn)}
    by_file = {}
    order = []
    for no, e in edits.items():
        s = segs[no]
        by_file.setdefault(s["chunk"], []).append((no, s, e))
        if s["chunk"] not in order:
            order.append(s["chunk"])
    for chunk in order:
        raw, eol, lines, idxs, p = read_chunk(chunk)
        items = by_file[chunk]
        for no, s, e in items:
            i = idxs[s["idx"] - 1]
            old = lines[i]
            if isinstance(e, list):
                cur = old
                for one in e:
                    if cur.count(one["find"]) != 1:
                        raise SystemExit("FIND 不唯一: %s %s#%d count=%d %r" % (
                            no, chunk, s["idx"], cur.count(one["find"]), one["find"]))
                    cur = cur.replace(one["find"], one["new"])
                lines[i] = cur
            elif isinstance(e, dict):
                find, new = e["find"], e["new"]
                if old.count(find) != 1:
                    raise SystemExit("FIND 不唯一: %s %s#%d count=%d %r" % (
                        no, chunk, s["idx"], old.count(find), find))
                lines[i] = old.replace(find, new)
            else:
                lines[i] = e
        d = os.path.join(BAK, "02_戒疏")
        if not os.path.isdir(d):
            os.makedirs(d)
        bp = os.path.join(d, chunk + "_b.txt")
        if not os.path.exists(bp):
            shutil.copy2(p, bp)
        with io.open(p, "w", encoding="utf-8", newline="") as f:
            f.write(eol.join(lines))
        print("寫入 %s：%d 段；備份 %s" % (chunk, len(items), os.path.basename(bp)))
        for no, s, e in items:
            print("  %s -> #%d" % (no, s["idx"]))


if __name__ == "__main__":
    if sys.argv[1] == "apply":
        nnn = sys.argv[2]
        efile = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, "edits_%s.json" % nnn)
        apply_edits(nnn, json.loads(rd(efile)))
    else:
        for n in sys.argv[2:]:
            dump(n)
