# -*- coding: utf-8 -*-
"""零頭批 7K 檢視助手。
用法:
  python _7k_ling_show.py dump 2536 2537 ...   # 產生 _r7k_view7/ling_NNNN.txt
  python _7k_ling_show.py seg 2536 108 109     # 印指定段（原文/材料/現行）
"""
import os, sys, re, io

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
X7 = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out")
VIEW = os.path.join(ROOT, "AI語譯", "_work", "review", "_r7k_view7")

_cache = {}


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


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


def parse_x7(nnn):
    p = os.path.join(X7, "校閱_%s.txt" % nnn)
    lines = rd(p).replace("\r\n", "\n").split("\n")
    segs, cur = [], None
    for ln in lines:
        m = re.match(r"^【(\d{3,4}-\d{4})】\s*(\S+)#(\d+)\s*$", ln.strip())
        if m:
            cur = {"no": m.group(1), "chunk": m.group(2), "idx": int(m.group(3)), "src": "", "tr": ""}
            segs.append(cur)
            continue
        if cur is not None:
            if ln.startswith("【原文】"):
                cur["src"] = ln[4:].strip()
            elif ln.startswith("【譯文】"):
                cur["tr"] = ln[4:].strip()
    return segs


def dump(nnn):
    if not os.path.isdir(VIEW):
        os.makedirs(VIEW)
    segs = parse_x7(nnn)
    buf = ["#" * 12 + " 檔 %s（%d 段）" % (nnn, len(segs)) + "#" * 12]
    cur_chunk = None
    for s in segs:
        if s["chunk"] != cur_chunk:
            cur_chunk = s["chunk"]
            raw, eol, lines, idxs, p = read_chunk(cur_chunk)
            buf.append("\n@@ chunk = %s  (EOL=%s, 非空行=%d)" % (cur_chunk, eol == "\r\n" and "CRLF" or "LF", len(idxs)))
        i = idxs[s["idx"] - 1]
        c = lines[i].strip()
        same = (c == s["tr"])
        buf.append("\n--- %s  #%d  %s" % (s["no"], s["idx"], "現行=材料" if same else "※現行已異動"))
        buf.append("[原文] " + s["src"])
        buf.append("[材料] " + s["tr"])
        if not same:
            buf.append("[現行] " + c)
    out = os.path.join(VIEW, "ling_%s.txt" % nnn)
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(buf) + "\n")
    print("wrote " + out)


def seg(nnn, want):
    segs = parse_x7(nnn)
    d = {str(s["idx"]): s for s in segs}
    for w in want:
        s = d.get(str(w))
        if not s:
            print("(無此段 %s #%s)" % (nnn, w))
            continue
        raw, eol, lines, idxs, p = read_chunk(s["chunk"])
        c = lines[idxs[s["idx"] - 1]].strip()
        same = (c == s["tr"])
        print("\n--- %s  #%d  %s" % (s["no"], s["idx"], "現行=材料" if same else "※現行已異動"))
        print("[原文] " + s["src"])
        print("[材料] " + s["tr"])
        if not same:
            print("[現行] " + c)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "dump":
        for n in sys.argv[2:]:
            dump(n)
    elif cmd == "seg":
        seg(sys.argv[2], sys.argv[3:])
