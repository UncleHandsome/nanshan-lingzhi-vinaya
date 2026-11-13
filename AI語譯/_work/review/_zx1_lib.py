# -*- coding: utf-8 -*-
"""7K 資持記 上一上 校閱輔助：材料讀取、段落級替換、備份、驗證。"""
import io
import json
import os
import re
import shutil
import sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
BOOK = "資持記"
OUTDIR = os.path.join(ROOT, "AI語譯", "out", BOOK)
MATDIR = os.path.join(ROOT, "校閱_7K")
BAKDIR = os.path.join(ROOT, "歸檔", "7K卷修正前", BOOK)

SEG_RE = re.compile(r"^【(\d{4})-(\d{4})】(\S+)#(\d+)\s*$")


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def wr(p, s):
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def mat(n):
    t = rd(os.path.join(MATDIR, u"校閱_%d.txt" % n))
    segs = []
    cur = None
    buf = {"原文": [], "譯文": []}

    def flush():
        if cur is not None:
            cur["orig"] = "\n".join(buf["原文"]).strip()
            cur["trans"] = "\n".join(buf["譯文"]).strip()
            segs.append(cur)

    for ln in t.split("\n"):
        m = SEG_RE.match(ln.strip())
        if m:
            flush()
            cur = {"idx": m.group(1), "seg": m.group(2),
                   "chunk": m.group(3).split("/")[-1], "para": int(m.group(4))}
            buf = {"原文": [], "譯文": []}
            continue
        if cur is None:
            continue
        s = ln.strip()
        if s.startswith("【原文】"):
            buf["原文"].append(s[len("【原文】"):])
        elif s.startswith("【譯文】"):
            buf["譯文"].append(s[len("【譯文】"):])
        elif s and buf["原文"] and not buf["譯文"]:
            buf["原文"].append(s)
        elif s:
            buf["譯文"].append(s)
    flush()
    return segs


def sep(t):
    return "\r\n\r\n" if "\r\n" in t else "\n\n"


def paras(chunk):
    t = rd(os.path.join(OUTDIR, chunk + ".txt"))
    return t, sep(t)


def para(chunk, n):
    t, s = paras(chunk)
    return t.split(s)[n - 1]


def backup(chunk):
    os.makedirs(BAKDIR, exist_ok=True)
    src = os.path.join(OUTDIR, chunk + ".txt")
    dst = os.path.join(BAKDIR, chunk + "_v.txt")
    if not os.path.exists(dst):
        shutil.copy2(src, dst)
        return dst
    return None


def apply(edits):
    """edits: list of dict(chunk, para, old, new). 精確取代，驗證必中且唯一。"""
    byfile = {}
    for e in edits:
        byfile.setdefault(e["chunk"], []).append(e)
    report = []
    for chunk, es in byfile.items():
        backup(chunk)
        t, s = paras(chunk)
        parts = t.split(s)
        before = len(parts)
        for e in es:
            i = e["para"] - 1
            old, new = e["old"], e["new"]
            c = parts[i].count(old)
            if c == 0:
                # 毗/毘 異寫容錯
                for a, b in (("毗", "毘"), ("毘", "毗")):
                    o2, n2 = old.replace(a, b), new.replace(a, b)
                    if parts[i].count(o2) == 1:
                        old, new, c = o2, n2, 1
                        break
            if c != 1:
                raise SystemExit(u"命中數異常 %s#%d count=%d old=%r" % (chunk, e["para"], c, old))
            parts[i] = parts[i].replace(old, new)
            report.append(u"%s#%d %d字->%d字" % (chunk, e["para"], len(old), len(new)))
        out = s.join(parts)
        wr(os.path.join(OUTDIR, chunk + ".txt"), out)
        t2, s2 = paras(chunk)
        assert len(t2.split(s2)) == before, "段數變動 " + chunk
    return report


def verify_material(n):
    bad = []
    for sg in mat(n):
        try:
            p = para(sg["chunk"], sg["para"])
        except IndexError:
            bad.append((sg["seg"], sg["chunk"], sg["para"], "para out of range"))
            continue
        if p.strip() != sg["trans"].strip():
            bad.append((sg["seg"], sg["chunk"], sg["para"], "material != out"))
    return bad


if __name__ == "__main__":
    if sys.argv[1] == "show":
        for sg in mat(int(sys.argv[2])):
            print(u"【%s-%s】%s#%d" % (sg["idx"], sg["seg"], sg["chunk"], sg["para"]))
            print(u"原: " + sg["orig"])
            print(u"譯: " + sg["trans"])
            print()
    elif sys.argv[1] == "apply":
        dat = json.load(io.open(sys.argv[2], encoding="utf-8"))
        for r in apply(dat):
            print(r)
    elif sys.argv[1] == "verify":
        for n in range(int(sys.argv[2]), int(sys.argv[3]) + 1):
            b = verify_material(n)
            print(n, "OK" if not b else b)
    elif sys.argv[1] == "stat":
        for chunk in sorted(set(sg["chunk"] for n in range(int(sys.argv[2]), int(sys.argv[3]) + 1) for sg in mat(n))):
            t, s = paras(chunk)
            print(chunk, len(t.split(s)), "段")
