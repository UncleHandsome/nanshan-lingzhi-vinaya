# -*- coding: utf-8 -*-
"""resp 條目抽取（容忍多種標題格式）+ 摘要。用法:
  python _rv_dig2.py 895 896 ...      # 產生 _rv_view/dig_NNN.txt
"""
import os, sys, re, io

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
sys.path.insert(0, os.path.join(ROOT, "AI語譯", "_work", "review"))
from _rv_kit import parse_x7, cur_of  # noqa

RESP = os.path.join(ROOT, "batch_qwen", "r7k")
VIEW = os.path.join(ROOT, "AI語譯", "_work", "review", "_rv_view")

ERR = re.compile(r"誤|錯|讀反|相反|顛倒|反了|生造|失義|丟[了失]|窄|偏離|主語|指代|對象|因果|範圍|術語|專名|法數|衍|添譯|增譯|應為|應作|不符|矛盾|不通|講反|理解錯|坐實|張冠李戴|無據|原意|必改|必查|泛譯|意譯|失準|倒置|主體")
SEGNO = re.compile(r"\d{3,4}-\d{4}")
LEAD = re.compile(r"^[\s#*\-•·★☆❗⚠△○●◆■□｜|]*")
NUMPFX = re.compile(r"^(?:\d+[.、)]\s*)?")


def header_segs(line):
    """若此行是段標題，回傳段號清單，否則 None"""
    s = line.strip()
    s2 = LEAD.sub("", s)
    s2 = NUMPFX.sub("", s2)
    # 形如 【895-0001】...
    m = re.match(r"^【(\d{3,4}-\d{4})】", s2)
    if m and len(s) < 90:
        return SEGNO.findall(s2[:40])
    # 形如 895-0001  或 895-0001 標題
    m = re.match(r"^(\d{3,4}-\d{4})\s*[：:，,、]?\s*", s2)
    if m and len(s) < 90 and len(m.group(0)) <= 12:
        return SEGNO.findall(s2[:40])
    return None


def split_items(text):
    out, cur, buf = [], None, []
    for ln in text.split("\n"):
        s = ln.strip()
        if s == "---":
            continue
        h = header_segs(s)
        if h:
            if buf and cur:
                out.append((cur, "\n".join(buf).strip()))
            cur, buf = h, [s]
            continue
        if cur is None:
            continue
        if re.match(r"^##\s", s) and not SEGNO.search(s[:30]):
            if buf:
                out.append((cur, "\n".join(buf).strip()))
            cur, buf = None, []
            continue
        buf.append(ln.rstrip())
    if buf and cur:
        out.append((cur, "\n".join(buf).strip()))
    return out


def dig(nnn):
    p = os.path.join(RESP, "resp_%s.txt" % nnn)
    text = io.open(p, encoding="utf-8").read()
    # 短式段號【0003】→【NNN-0003】
    text = re.sub(r"(?m)^([\s#*\-•·]*)(【)(\d{4})(】)",
                  lambda m: m.group(1) + "【" + nnn + "-" + m.group(3) + "】", text)
    segs = parse_x7(nnn)
    d = {s["no"]: s for s in segs}
    items = split_items(text)
    buf = ["#" * 8 + " %s " % nnn + "#" * 8]
    head = re.split(r"\n\s*---", text)[0].strip()
    buf.append("[開頭] " + head)
    seen = set()
    nflag = 0
    for nos, body in items:
        for no in nos:
            s = d.get(no)
            if not s:
                buf.append("\n=== %s [無此段] %s" % (no, body[:300]))
                continue
            seen.add(no)
        if not ERR.search(body):
            continue
        for no in nos:
            s = d.get(no)
            if not s:
                continue
            nflag += 1
            c = cur_of(s)
            st = "同" if c == s["tr"] else "改"
            buf.append("\n=== %s [%s]" % (no, st))
            src = s["src"]
            buf.append("[原文] " + (src if len(src) <= 200 else src[:200] + "…"))
            if st == "改":
                buf.append("[現行] " + c)
            buf.append("[意見] " + (body if len(body) <= 450 else body[:450] + "…"))
    miss = [s["no"] for s in segs if s["no"] not in seen]
    if miss:
        buf.append("\n[意見未提段] " + " ".join(miss))
    out = os.path.join(VIEW, "dig_%s.txt" % nnn)
    io.open(out, "w", encoding="utf-8").write("\n".join(buf) + "\n")
    return nflag, len(segs)


if __name__ == "__main__":
    tot = 0
    for n in sys.argv[1:]:
        f, nseg = dig(n)
        tot += f
        print("%s flag=%d / %d段" % (n, f, nseg))
    print("total=%d" % tot)
