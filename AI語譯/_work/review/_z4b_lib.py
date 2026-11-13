# -*- coding: utf-8 -*-
"""7K 資持記 下四_b helpers (2021-2045)."""
import os, re, sys, json, shutil

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
MAT = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out", "資持記")
RESP = os.path.join(ROOT, "batch_qwen", "r7k")
VIEW = os.path.join(ROOT, "AI語譯", "_work", "review", "_z4b_view")
BAK = os.path.join(ROOT, "歸檔", "7K卷修正前", "資持記")
LOG = os.path.join(ROOT, "AI語譯", "_work", "review", "_z4b_log.jsonl")


def read(p):
    with open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def norm(t):
    return t.replace("\r\n", "\n").replace("\r", "\n")


def read_out(chunk):
    raw = read(os.path.join(OUT, chunk + ".txt"))
    eol = "\r\n" if "\r\n" in raw else ("\r" if "\r" in raw else "\n")
    lines = norm(raw).split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    return lines, eol


def mat_map(n):
    t = norm(read(os.path.join(MAT, "校閱_%d.txt" % n)))
    items = []
    pat = re.compile(r"【(\d{4}-\d{4})】資持記/(\S+?)#(\d+)\n【原文】(.*?)\n【譯文】(.*?)(?=\n\n【\d{4}-\d{4}】|\s*\Z)", re.S)
    for m in pat.finditer(t):
        items.append(dict(seg=m.group(1), chunk=m.group(2), idx=int(m.group(3)),
                          src=m.group(4).strip(), tr=m.group(5).strip()))
    return items


def view(n):
    os.makedirs(VIEW, exist_ok=True)
    buf = ["#" * 10 + " 意見 resp_%d " % n + "#" * 10]
    rp = os.path.join(RESP, "resp_%d.txt" % n)
    buf.append(read(rp).strip() if os.path.exists(rp) else "(缺意見)")
    items = mat_map(n)
    buf.append("")
    buf.append("#" * 10 + " 段落 %d（%d 段）" % (n, len(items)) + "#" * 10)
    cache = {}
    for it in items:
        c = it["chunk"]
        if c not in cache:
            cache[c] = read_out(c)
        lines, eol = cache[c]
        ne = [(i, l) for i, l in enumerate(lines) if l.strip()]
        cur = ne[it["idx"] - 1][1].strip()
        same = cur == it["tr"]
        buf.append("\n--- %s  %s #%d  %s" % (it["seg"], c, it["idx"], "現行=材料" if same else "※現行已異動"))
        buf.append("[原文] " + it["src"])
        buf.append("[譯文] " + cur)
        if not same:
            buf.append("[材料] " + it["tr"])
    p = os.path.join(VIEW, "v_%d.txt" % n)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(buf) + "\n")
    print(p)


def backup(chunk):
    os.makedirs(BAK, exist_ok=True)
    dst = os.path.join(BAK, chunk + "_v.txt")
    if not os.path.exists(dst):
        shutil.copyfile(os.path.join(OUT, chunk + ".txt"), dst)
        return dst
    return None


def apply(spec_path):
    spec = json.load(open(spec_path, encoding="utf-8"))
    bychunk = {}
    for n in sorted(spec):
        for e in spec[n]["edits"]:
            bychunk.setdefault(spec[n]["chunk"], []).append((n, e))
    log = []
    for chunk, edits in bychunk.items():
        lines, eol = read_out(chunk)
        ne = [(i, l) for i, l in enumerate(lines) if l.strip()]
        for n, e in edits:
            ln = ne[e["idx"] - 1][0]
            cur = lines[ln]
            c = cur.count(e["old"])
            if c != 1:
                raise SystemExit("檔%s seg#%d old count=%d\n%r" % (n, e["idx"], c, e["old"]))
            lines[ln] = cur.replace(e["old"], e["new"])
            log.append(dict(n=int(n), chunk=chunk, idx=e["idx"], cat=e.get("cat", ""),
                            old=e["old"], new=e["new"], why=e.get("why", "")))
        backup(chunk)
        out = os.path.join(OUT, chunk + ".txt")
        with open(out, "w", encoding="utf-8", newline="") as f:
            f.write(eol.join(lines) + eol)
        print("WROTE", chunk, len(edits))
    with open(LOG, "a", encoding="utf-8") as f:
        for r in log:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("EDITS", len(log))


def show(n, extra=0):
    """print raw material segments only"""
    items = mat_map(n)
    for it in items:
        print("=== %s %s#%d" % (it["seg"], it["chunk"], it["idx"]))
        print("[原文]", it["src"])
        print("[譯文]", it["tr"])


def spot(chunk, a, b=None):
    lines, eol = read_out(chunk)
    ne = [l for l in lines if l.strip()]
    b = b or a
    out = []
    for i in range(a, b + 1):
        out.append("--- %s #%d\n%s" % (chunk, i, ne[i - 1]))
    p = os.path.join(VIEW, "spot_%s_%d_%d.txt" % (chunk, a, b))
    os.makedirs(VIEW, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print(p)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "view":
        for a in sys.argv[2:]:
            view(int(a))
    elif cmd == "show":
        show(int(sys.argv[2]))
    elif cmd == "spot":
        spot(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else None)
