# -*- coding: utf-8 -*-
"""戒疏否決複審（844-894）digest：抽 resp 條目、比對現行、先篩潤飾/加註/體例。
用法: python _rv2_dig.py 844 845 ...        -> _rv2/dig_NNN.txt
      python _rv2_dig.py all
"""
import os, sys, re, io

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
sys.path.insert(0, os.path.join(ROOT, "AI語譯", "_work", "review"))
from _rv_kit import parse_x7, cur_of  # noqa

RESP = os.path.join(ROOT, "batch_qwen", "r7k")
VIEW = os.path.join(ROOT, "AI語譯", "_work", "review", "_rv2")

SEGNO = re.compile(r"\d{3,4}-\d{4}")
LEAD = re.compile(r"^[\s#*\-•·★☆❗⚠△○●◆■□｜|]*")
NUMPFX = re.compile(r"^(?:\d+[.、)]\s*)?")

# 四類：術語/主客/因果/範圍 + 經文 + 生造詞
CAT = re.compile(r"術語|名相|專名|法數|讀反|相反|顛倒|倒置|主語|主體|主客|對象|所指|指代|"
                 r"因果|範圍|窄|泛|籠統|經文|戒本|律文|生造|失義|誤指|誤讀|張冠李戴|坐實|"
                 r"增添|增譯|添譯|無據|原文所無|擅改|科判|層級|位階")
# 跳過：潤飾/加註/體例/建議語氣
SKIP = re.compile(r"加註|補註|夾註|註明|校註|小註|括號|引號|篇題|體例|潤飾|語感|讀來|拗口|"
                  r"統一|一致性|建議|可考慮|不妨|似乎|稍嫌|略嫌|不夠精準|措辭|行文|句讀|標點|"
                  r"贅字|語氣|簡潔|順暢|通順|重複|斷句")


def header_segs(line):
    s = line.strip()
    s2 = NUMPFX.sub("", LEAD.sub("", s))
    m = re.match(r"^【(\d{3,4}-\d{4})】", s2)
    if m and len(s) < 90:
        return SEGNO.findall(s2[:40])
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
    text = re.sub(r"(?m)^([\s#*\-•·]*)(【)(\d{4})(】)",
                  lambda m: m.group(1) + "【" + nnn + "-" + m.group(3) + "】", text)
    segs = parse_x7(nnn)
    d = {s["no"]: s for s in segs}
    items = split_items(text)
    buf = []
    head = re.split(r"\n\s*---", text)[0].strip()
    buf.append("[開頭] " + head[:400])
    nrej = nin = 0
    for nos, body in items:
        st = None
        for no in nos:
            s = d.get(no)
            if not s:
                continue
            st = "改" if cur_of(s) != s["tr"] else "拒"
            if st == "拒":
                nrej += 1
                break
        if st is None:
            continue
        if not CAT.search(body) or SKIP.search(body):
            continue
        nin += 1
        for no in nos:
            s = d.get(no)
            if not s:
                continue
            src = s["src"]
            cur = cur_of(s)
            buf.append("\n=== %s [%s]" % (no, st))
            buf.append("[原文] " + src)
            buf.append("[現行] " + (cur if len(cur) <= 260 else cur[:260] + "…"))
            buf.append("[意見] " + (body if len(body) <= 420 else body[:420] + "…"))
            break
    if not os.path.isdir(VIEW):
        os.makedirs(VIEW)
    out = os.path.join(VIEW, "dig_%s.txt" % nnn)
    io.open(out, "w", encoding="utf-8", newline="\n").write("\n".join(buf) + "\n")
    return nrej, nin


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["all"]:
        args = [str(i) for i in range(844, 895)]
    tr = ti = 0
    for n in args:
        r, i = dig(n)
        tr += r
        ti += i
        print("%s 拒=%d 入審=%d" % (n, r, i))
    print("total 拒=%d 入審=%d" % (tr, ti))
