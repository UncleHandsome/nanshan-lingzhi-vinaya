# -*- coding: utf-8 -*-
"""戒疏否決複審助手（895-931）。
用法:
  python _rv_kit.py show 895 896 ...     # 產生 _rv_view/view_NNN.txt
  python _rv_kit.py seg 895 10 11        # 只印指定段
  python _rv_kit.py apply 11a_卷三上之二 edits.json
"""
import os, sys, re, json, shutil, io

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
X7 = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out")
BAK = os.path.join(ROOT, "歸檔", "7K卷修正前")
RESP = os.path.join(ROOT, "batch_qwen", "r7k")
VIEW = os.path.join(ROOT, "AI語譯", "_work", "review", "_rv_view")
BOOK = "02_戒疏"


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
            cur = {"no": m.group(1), "chunk": m.group(2).split("/", 1)[1], "idx": int(m.group(3)), "src": "", "tr": ""}
            segs.append(cur)
            continue
        if cur is not None:
            if ln.startswith("【原文】"):
                cur["src"] = ln[4:].strip()
            elif ln.startswith("【譯文】"):
                cur["tr"] = ln[4:].strip()
    return segs


_cache = {}


def read_chunk(chunk):
    if chunk in _cache:
        return _cache[chunk]
    p = os.path.join(OUT, BOOK, chunk + ".txt")
    raw = rd(p)
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    idxs = [i for i, l in enumerate(lines) if l.strip()]
    _cache[chunk] = (raw, eol, lines, idxs, p)
    return _cache[chunk]


def cur_of(seg):
    raw, eol, lines, idxs, p = read_chunk(seg["chunk"])
    return lines[idxs[seg["idx"] - 1]].strip()


def diffspan(a, b):
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    j = 0
    while j < n - i and a[-1 - j] == b[-1 - j]:
        j += 1
    return i, a[max(0, i - 12):len(a) - j + 12], b[max(0, i - 12):len(b) - j + 12]


def show(nnn):
    if not os.path.isdir(VIEW):
        os.makedirs(VIEW)
    buf = []
    rp = os.path.join(RESP, "resp_%s.txt" % nnn)
    buf.append("#" * 15 + " resp_%s " % nnn + "#" * 15)
    buf.append(rd(rp).strip() if os.path.exists(rp) else "(缺意見檔)")
    buf.append("")
    segs = parse_x7(nnn)
    buf.append("#" * 15 + " %s（%d 段）" % (nnn, len(segs)) + "#" * 15)
    for s in segs:
        c = cur_of(s)
        same = (c == s["tr"])
        buf.append("\n--- %s  #%d  %s" % (s["no"], s["idx"], "現行=材料" if same else "※現行已異動"))
        buf.append("[原文] " + s["src"])
        if same:
            buf.append("[現行] " + c)
        else:
            pos, x, y = diffspan(s["tr"], c)
            buf.append("[材料] " + s["tr"])
            buf.append("[現行] " + c)
            buf.append("[差異@%d] 材料…%s… / 現行…%s…" % (pos, x, y))
    out = os.path.join(VIEW, "view_%s.txt" % nnn)
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(buf) + "\n")
    print("wrote " + out)


def seg(nnn, want):
    segs = parse_x7(nnn)
    d = {s["no"].split("-")[1]: s for s in segs}
    for w in want:
        s = d.get(w.zfill(4))
        if not s:
            print("(無此段 %s)" % w)
            continue
        c = cur_of(s)
        same = (c == s["tr"])
        print("\n--- %s  #%d  %s" % (s["no"], s["idx"], "現行=材料" if same else "※現行已異動"))
        print("[原文] " + s["src"])
        if same:
            print("[現行] " + c)
        else:
            pos, x, y = diffspan(s["tr"], c)
            print("[材料] " + s["tr"])
            print("[現行] " + c)
            print("[差異@%d] 材料…%s… / 現行…%s…" % (pos, x, y))


def apply_edits(chunk, efile):
    """edits.json: [{no, idx?, find, new}]  (find 必須在該行唯一)"""
    edits = json.loads(rd(efile))
    raw, eol, lines, idxs, p = read_chunk(chunk)
    for e in edits:
        idx = e["idx"]
        i = idxs[idx - 1]
        old = lines[i]
        cur = old
        for one in (e["ops"] if "ops" in e else [e]):
            find, new = one["find"], one["new"]
            c = cur.count(find)
            if c != 1:
                raise SystemExit("FIND 不唯一/不存在: %s #%d count=%d %r" % (e.get("no"), idx, c, find))
            cur = cur.replace(find, new)
        if cur == old:
            raise SystemExit("無變化: %s #%d" % (e.get("no"), idx))
        lines[i] = cur
    d = os.path.join(BAK, BOOK)
    if not os.path.isdir(d):
        os.makedirs(d)
    bp = os.path.join(d, chunk + "_v.txt")
    if not os.path.exists(bp):
        shutil.copy2(p, bp)
        print("備份 %s" % bp)
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(eol.join(lines))
    print("寫入 %s：%d 段" % (chunk, len(edits)))
    _cache.pop(chunk, None)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "show":
        for n in sys.argv[2:]:
            show(n)
    elif cmd == "seg":
        seg(sys.argv[2], sys.argv[3:])
    elif cmd == "apply":
        apply_edits(sys.argv[2], sys.argv[3])
