# -*- coding: utf-8 -*-
"""卷二下之一 7K 校閱助手（檔 746-792）。
用法:
  python _r7k_z27.py scan               # 檢查材料/現行差異、chunk 分佈
  python _r7k_z27.py show 746 747 ...   # 產生 _r7k_view/view_NNN.txt
  python _r7k_z27.py apply <chunk> <edits.json>
"""
import os, sys, re, json, shutil, io

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
X7 = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out")
BAK = os.path.join(ROOT, "歸檔", "7K卷修正前")
RESP = os.path.join(ROOT, "batch_qwen", "r7k")
VIEW = os.path.join(ROOT, "AI語譯", "_work", "review", "_r7k_view")
FILES = list(range(746, 793))


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
            cur = {"no": m.group(1), "chunk": m.group(2), "idx": int(m.group(3)), "src": "", "tr": ""}
            segs.append(cur)
            continue
        if cur is not None:
            if ln.startswith("【原文】"):
                cur["src"] = ln[4:].strip()
            elif ln.startswith("【譯文】"):
                cur["tr"] = ln[4:].strip()
    return segs


def read_chunk(chunk):
    book, name = chunk.split("/", 1)
    p = os.path.join(OUT, book, name + ".txt")
    raw = rd(p)
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    idxs = [i for i, l in enumerate(lines) if l.strip()]
    return raw, eol, lines, idxs, p


def diffspan(a, b):
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    j = 0
    while j < n - i and a[-1 - j] == b[-1 - j]:
        j += 1
    return i, a[max(0, i - 8):len(a) - j + 8], b[max(0, i - 8):len(b) - j + 8]


def scan():
    cache = {}
    for n in FILES:
        segs = parse_x7(n)
        chunks = []
        same = diff = 0
        for s in segs:
            if s["chunk"] not in cache:
                cache[s["chunk"]] = read_chunk(s["chunk"])
            raw, eol, lines, idxs, p = cache[s["chunk"]]
            c = lines[idxs[s["idx"] - 1]].strip()
            if c == s["tr"]:
                same += 1
            else:
                diff += 1
                pos, x, y = diffspan(s["tr"], c)
                print("%s #%d DIFF@%d\n  材料…%s…\n  現行…%s…" % (s["no"], s["idx"], pos, x, y))
            if s["chunk"] not in chunks:
                chunks.append(s["chunk"])
        print("%d  seg=%d same=%d diff=%d chunks=%s" % (n, len(segs), same, diff, ",".join(chunks)))
    for ch in cache:
        raw, eol, lines, idxs, p = cache[ch]
        print("chunk %s  非空行=%d  EOL=%s" % (ch, len(idxs), "CRLF" if eol == "\r\n" else "LF"))


def show(nnn):
    if not os.path.isdir(VIEW):
        os.makedirs(VIEW)
    buf = []
    rp = os.path.join(RESP, "resp_%s.txt" % nnn)
    buf.append("#" * 18 + " 意見 resp_%s " % nnn + "#" * 18)
    buf.append(rd(rp).strip() if os.path.exists(rp) else "(缺意見檔)")
    buf.append("")
    segs = parse_x7(nnn)
    buf.append("#" * 18 + " 段落 %s（%d 段）" % (nnn, len(segs)) + "#" * 18)
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
        buf.append("[材料譯文] " + s["tr"])
        if not same:
            pos, x, y = diffspan(s["tr"], c)
            buf.append("[現行譯文] " + c)
            buf.append("[差異@%d] 材料…%s… / 現行…%s…" % (pos, x, y))
    out = os.path.join(VIEW, "view_%s.txt" % nnn)
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(buf) + "\n")
    print("wrote " + out)


def apply_edits(chunk, efile):
    edits = json.loads(rd(efile))
    segs = {}
    for n in FILES:
        for s in parse_x7(n):
            if s["chunk"] == chunk:
                segs[s["no"]] = s
    raw, eol, lines, idxs, p = read_chunk(chunk)
    changed = 0
    for no, e in sorted(edits.items()):
        if not e:
            continue
        idx = e.get("idx") if isinstance(e, dict) and "idx" in e else segs[no]["idx"]
        i = idxs[idx - 1]
        old = lines[i]
        cur = old
        ops = e["ops"] if isinstance(e, dict) and "ops" in e else e
        for one in ops:
            find, new = one["find"], one["new"]
            c = cur.count(find)
            if c != 1:
                raise SystemExit("FIND 不唯一/不存在: %s #%d count=%d %r" % (no, idx, c, find))
            cur = cur.replace(find, new)
        if cur == old:
            raise SystemExit("無變化: %s #%d" % (no, idx))
        lines[i] = cur
        changed += 1
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
    print("寫入 %s：%d 段（ops 檔 %s）" % (chunk, changed, os.path.basename(efile)))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "scan":
        scan()
    elif cmd == "show":
        for n in sys.argv[2:]:
            show(n)
    elif cmd == "apply":
        apply_edits(sys.argv[2], sys.argv[3])
