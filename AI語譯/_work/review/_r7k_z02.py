# -*- coding: utf-8 -*-
"""資持記 上一下 7K 校閱助手（檔 1352-1419）。
用法:
  python _r7k_z02.py show 1352 [1353 ...]   # 產生 _r7k_view/z02_1352.txt
  python _r7k_z02.py seg 1352 1 3           # 只印指定段（材料原文/譯文/現行）
  python _r7k_z02.py apply 資持記/02a_上一下 e.json
e.json 格式: {"1352-0001": {"ops":[{"find":"..","new":".."}], "kind":"義理|潤飾"}}
"""
import os, sys, re, json, shutil, io

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
X7 = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out")
BAK = os.path.join(ROOT, "歸檔", "7K卷修正前")
RESP = os.path.join(ROOT, "batch_qwen", "r7k")
VIEW = os.path.join(ROOT, "AI語譯", "_work", "review", "_r7k_view")
LO = 1352
HI = 1419


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


def show(nnn):
    if not os.path.isdir(VIEW):
        os.makedirs(VIEW)
    buf = []
    rp = os.path.join(RESP, "resp_%s.txt" % nnn)
    buf.append("#" * 20 + " 意見 resp_%s " % nnn + "#" * 20)
    buf.append(rd(rp).strip() if os.path.exists(rp) else "(缺意見檔)")
    buf.append("")
    segs = parse_x7(nnn)
    buf.append("#" * 20 + " 段落 %s（%d 段）" % (nnn, len(segs)) + "#" * 20)
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
            buf.append("[現行譯文] " + c)
    out = os.path.join(VIEW, "z02_%s.txt" % nnn)
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
        raw, eol, lines, idxs, p = read_chunk(s["chunk"])
        c = lines[idxs[s["idx"] - 1]].strip()
        same = (c == s["tr"])
        print("\n--- %s  #%d  %s" % (s["no"], s["idx"], "現行=材料" if same else "※現行已異動"))
        print("[原文] " + s["src"])
        print("[材料譯文] " + s["tr"])
        if not same:
            print("[現行譯文] " + c)


def build_map():
    m = {}
    for n in range(LO, HI + 1):
        for s in parse_x7(n):
            m[s["no"]] = s
    return m


def apply_edits(chunk, efile):
    segs = {k: v for k, v in build_map().items() if v["chunk"] == chunk}
    edits = json.loads(rd(efile))
    raw, eol, lines, idxs, p = read_chunk(chunk)
    nseg = 0
    for no, e in sorted(edits.items()):
        if no not in segs:
            raise SystemExit("段號不在本 chunk: %s" % no)
        idx = segs[no]["idx"]
        i = idxs[idx - 1]
        old = lines[i]
        cur = old
        ops = e.get("ops") if isinstance(e, dict) and "ops" in e else e
        for one in ops:
            find, new = one["find"], one["new"]
            c = cur.count(find)
            if c != 1:
                raise SystemExit("FIND 不唯一/不存在: %s #%d count=%d %r" % (no, idx, c, find))
            cur = cur.replace(find, new)
        if cur == old:
            raise SystemExit("無變化: %s #%d" % (no, idx))
        lines[i] = cur
        nseg += 1
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
    nz = sum(1 for l in lines if l.strip())
    print("寫入 %s：%d 段（總 %d 段）" % (chunk, nseg, nz))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "show":
        for n in sys.argv[2:]:
            show(n)
    elif cmd == "seg":
        seg(sys.argv[2], sys.argv[3:])
    elif cmd == "apply":
        apply_edits(sys.argv[2], sys.argv[3])
