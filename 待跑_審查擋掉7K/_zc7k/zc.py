# -*- coding: utf-8 -*-
"""資持記 7K 擋檔助手。
用法:
  python zc.py show NNN          # 印出材料各段原文/材料譯文/現行 out 文字
  python zc.py apply NNN         # 套用 _zc7k/edits_NNN.json
"""
import os, sys, re, json, shutil, io

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
X7 = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out")
BAK = os.path.join(ROOT, "歸檔", "7K擋檔修正前", "資持記")
HERE = os.path.dirname(os.path.abspath(__file__))


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def parse_x7(nnn):
    p = os.path.join(X7, "校閱_%s.txt" % nnn)
    lines = rd(p).replace("\r\n", "\n").split("\n")
    segs = []
    cur = None
    for ln in lines:
        m = re.match(r"^【(\d{3}-\d{4})】\s*(\S+)#(\d+)\s*$", ln.strip())
        if m:
            cur = {"no": m.group(1), "chunk": m.group(2), "idx": int(m.group(3)),
                   "src": "", "tr": ""}
            segs.append(cur)
            continue
        if cur is not None:
            if ln.startswith("【原文】"):
                cur["src"] = ln[4:]
            elif ln.startswith("【譯文】"):
                cur["tr"] = ln[4:]
    return segs


def read_chunk(chunk):
    book, name = chunk.split("/", 1)
    p = os.path.join(OUT, book, name + ".txt")
    raw = rd(p)
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    idxs = [i for i, l in enumerate(lines) if l.strip()]
    return raw, eol, lines, idxs, p


def cur_text(seg):
    raw, eol, lines, idxs, p = read_chunk(seg["chunk"])
    i = idxs[seg["idx"] - 1]
    return lines[i].strip()


def firstdiff(a, b):
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    j = 0
    while j < n - i and a[-1 - j] == b[-1 - j]:
        j += 1
    return a[max(0, i - 8):len(a) - j + 8], b[max(0, i - 8):len(b) - j + 8], i


def show(nnn):
    buf = []
    buf.append("=" * 20 + " 段落 " + nnn + " " + "=" * 20)
    segs = parse_x7(nnn)
    for s in segs:
        c = cur_text(s)
        same = (c == s["tr"])
        buf.append("\n--- %s  %s#%d  %s" % (s["no"], s["chunk"], s["idx"],
                                           "現行=材料" if same else "※現行已異動"))
        buf.append("[原文] " + s["src"])
        if not same:
            a, b, i = firstdiff(s["tr"], c)
            buf.append("[材料譯文] " + s["tr"])
            buf.append("[現行譯文] " + c)
            buf.append("[差異] 位置%d 材料…%s… / 現行…%s…" % (i, a, b))
        else:
            buf.append("[譯文] " + c)
    out = os.path.join(HERE, "view_%s.txt" % nnn)
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(buf) + "\n")
    print("wrote " + out)


def apply_edits(nnn, edits):
    segs = {s["no"]: s for s in parse_x7(nnn)}
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
                        raise SystemExit("FIND 不唯一或不存在: %s in %s#%d (count=%d) %r"
                                         % (no, chunk, s["idx"], cur.count(one["find"]), one["find"]))
                    cur = cur.replace(one["find"], one["new"])
                lines[i] = cur
            elif isinstance(e, dict):
                find, new = e["find"], e["new"]
                if old.count(find) != 1:
                    raise SystemExit("FIND 不唯一或不存在: %s in %s#%d (count=%d)"
                                     % (no, chunk, s["idx"], old.count(find)))
                lines[i] = old.replace(find, new)
            else:
                lines[i] = e
        book, name = chunk.split("/", 1)
        d = os.path.join(BAK, book)
        if not os.path.isdir(d):
            os.makedirs(d)
        bp = os.path.join(d, name + "_a.txt")
        if not os.path.exists(bp):
            shutil.copy2(p, bp)
        with io.open(p, "w", encoding="utf-8", newline="") as f:
            f.write(eol.join(lines))
        print("寫入 %s：%d 段；備份 %s" % (chunk, len(items), os.path.relpath(bp, ROOT)))
        for no, s, e in items:
            print("  %s -> #%d" % (no, s["idx"]))


if __name__ == "__main__":
    if sys.argv[1] == "apply":
        nnn = sys.argv[2]
        efile = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, "edits_%s.json" % nnn)
        edits = json.loads(rd(efile))
        apply_edits(nnn, edits)
    else:
        show(sys.argv[1])
