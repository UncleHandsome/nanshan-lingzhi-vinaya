# -*- coding: utf-8 -*-
"""否決複審助手（02_戒疏 卷一下之一, 551-591）。
用法:
  python _jx_tool.py map 551 552 ...          # 檔號 -> 段號 chunk#idx 清單
  python _jx_tool.py find 03a 經文            # 現行譯文含字串 -> 段號/原文/現行
  python _jx_tool.py seg 551 1 7 9            # 指定段：原文/材料/現行(+差異片段)
  python _jx_tool.py dump 551 552             # 每段只給 段號/原文/現行（材料已併入與否標記）
  python _jx_tool.py apply <NNN> <edits.json> # {段號:[{find,new}...]}
"""
import os, sys, re, json, io, shutil, difflib

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
X7 = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out")
BAK = os.path.join(ROOT, "歸檔", "7K卷修正前")
RESP = os.path.join(ROOT, "batch_qwen", "r7k")


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


_cache = {}


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


def cur_of(seg):
    raw, eol, lines, idxs, p = read_chunk(seg["chunk"])
    return lines[idxs[seg["idx"] - 1]].strip()


def cmd_map(nums):
    for n in nums:
        segs = parse_x7(n)
        print("%s\t%d\t%s" % (n, len(segs), " ".join("%s#%d" % (s["chunk"].split("/")[-1], s["idx"]) for s in segs[:3]) + (" ..." if len(segs) > 3 else "")))


def cmd_find(chunk, pat):
    for n in range(551, 592):
        if not os.path.exists(os.path.join(X7, "校閱_%s.txt" % n)):
            continue
        for s in parse_x7(n):
            if s["chunk"].split("/")[-1].split("_")[0] != chunk:
                continue
            c = cur_of(s)
            if pat in c:
                print("--- %s  %s#%d" % (s["no"], s["chunk"], s["idx"]))
                print("[原文] " + s["src"])
                print("[現行] " + c)


def diff_frag(a, b, w=14):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    out = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        out.append("%s｜材料…%s…→現行…%s…" % (
            tag, a[max(0, i1 - w):min(len(a), i2 + w)], b[max(0, j1 - w):min(len(b), j2 + w)]))
    return " ; ".join(out) if out else "(無差異)"


def cmd_seg(nnn, ids):
    segs = {s["no"]: s for s in parse_x7(nnn)}
    for i in ids:
        no = "%s-%04d" % (nnn, int(i))
        s = segs.get(no)
        if not s:
            print("(無此段 %s)" % no)
            continue
        c = cur_of(s)
        print("--- %s  %s#%d" % (no, s["chunk"], s["idx"]))
        print("[原文] " + s["src"])
        if c != s["tr"]:
            print("[材料] " + s["tr"])
            print("[現行] " + c)
            print("[差] " + diff_frag(s["tr"], c))
        else:
            print("[現行] " + c)


def cmd_q(specs):
    """q 557:1,4,7 558:2"""
    for spec in specs:
        nnn, ids = spec.split(":")
        segs = {s["no"]: s for s in parse_x7(nnn)}
        for i in ids.split(","):
            no = "%s-%04d" % (nnn, int(i))
            s = segs.get(no)
            if not s:
                print("(無 %s)" % no)
                continue
            c = cur_of(s)
            print("--- %s %s#%d%s" % (no, s["chunk"].split("/")[-1], s["idx"], "" if c == s["tr"] else " ※已改"))
            print("[原] " + s["src"])
            print("[現] " + c)


def cmd_dump(nums, pat=None):
    for n in nums:
        segs = parse_x7(n)
        print("######## %s（%d 段）" % (n, len(segs)))
        for s in segs:
            c = cur_of(s)
            same = "" if c == s["tr"] else "  ※已改"
            if pat and pat not in c and pat not in s["src"]:
                continue
            print("-- %s %s#%d%s" % (s["no"], s["chunk"].split("/")[-1], s["idx"], same))
            print("[原] " + s["src"])
            print("[現] " + c)
            if c != s["tr"]:
                print("[差] " + diff_frag(s["tr"], c))


def cmd_apply(nnn, efile):
    edits = json.loads(rd(efile).lstrip("\ufeff"))
    by_chunk = {}
    for no, e in sorted(edits.items()):
        pf = no.split("-")[0]
        segs = {s["no"]: s for s in parse_x7(pf)}
        if no not in segs:
            raise SystemExit("無此段 " + no)
        by_chunk.setdefault(segs[no]["chunk"], []).append((no, segs[no], e))
    total = 0
    for chunk, items in by_chunk.items():
        raw, eol, lines, idxs, p = read_chunk(chunk)
        for no, s, e in items:
            i = idxs[s["idx"] - 1]
            old = lines[i]
            cur = old
            ops = e["ops"] if isinstance(e, dict) and "ops" in e else e
            for one in ops:
                find, new = one["find"], one["new"]
                c = cur.count(find)
                if c != 1:
                    raise SystemExit("FIND 不唯一/不存在: %s %r count=%d" % (no, find, c))
                cur = cur.replace(find, new)
            if cur == old:
                raise SystemExit("無變化: " + no)
            lines[i] = cur
            total += 1
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
        print("寫入 %s：%d 段" % (chunk, len(items)))
    print("合計 %d 段" % total)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "map":
        cmd_map(sys.argv[2:])
    elif cmd == "find":
        cmd_find(sys.argv[2], sys.argv[3])
    elif cmd == "seg":
        cmd_seg(sys.argv[2], sys.argv[3:])
    elif cmd == "q":
        cmd_q(sys.argv[2:])
    elif cmd == "dump":
        cmd_dump(sys.argv[2:])
    elif cmd == "apply":
        cmd_apply(sys.argv[2], sys.argv[3])



