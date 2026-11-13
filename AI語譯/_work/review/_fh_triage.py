# -*- coding: utf-8 -*-
"""否決複審 triage：列出各檔意見區塊、所引段、該段是否已改（現行 != 材料）。"""
import os, re, io, json, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
REVIEW = os.path.join(ROOT, "AI語譯", "_work", "review")
X7 = os.path.join(ROOT, "校閱_7K")
OUT = os.path.join(ROOT, "AI語譯", "out")
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


def read_chunk(chunk):
    book, name = chunk.split("/", 1)
    p = os.path.join(OUT, book, name + ".txt")
    raw = rd(p)
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    idxs = [i for i, l in enumerate(lines) if l.strip()]
    return lines, idxs


def segstatus(segs, cache):
    out = {}
    for s in segs:
        if s["chunk"] not in cache:
            cache[s["chunk"]] = read_chunk(s["chunk"])
        lines, idxs = cache[s["chunk"]]
        cur = lines[idxs[s["idx"] - 1]].strip()
        out[s["no"]] = (cur != s["tr"], cur, s["tr"], s["src"], s["chunk"], s["idx"])
    return out


def blocks(txt):
    """以空行分段，合併連續行。"""
    bs = []
    for para in re.split(r"\n\s*\n", txt):
        p = para.strip()
        if p:
            bs.append(p)
    return bs


def main(nnn):
    rp = os.path.join(RESP, "resp_%s.txt" % nnn)
    if not os.path.exists(rp):
        print("(缺 resp_%s)" % nnn)
        return
    txt = rd(rp).replace("\r\n", "\n")
    segs = parse_x7(nnn)
    allrefs = set(re.findall(r"(\d{3,4}-\d{4})", txt))
    byno = {s["no"]: s for s in segs}
    cache = {}
    st = segstatus(segs, cache)
    print("=" * 20, nnn, "=" * 20)
    print("意見引用段：%d，已改 %d：%s" % (
        len(allrefs),
        sum(1 for n in allrefs if n in st and st[n][0]),
        ",".join(sorted(n for n in allrefs if n in st and st[n][0]))))
    for i, b in enumerate(blocks(txt), 1):
        refs = sorted(set(re.findall(r"(\d{3,4}-\d{4})", b)))
        if not refs:
            continue
        changed = [r for r in refs if r in st and st[r][0]]
        flag = "已改" if changed else "未改"
        if len(changed) == len(refs):
            continue  # 全部引用段都已改，跳過
        head = re.sub(r"\s+", " ", b)[:120]
        print("\n[%02d][%s] refs=%s changed=%s" % (i, flag, ",".join(refs), ",".join(changed)))
        print(head)


if __name__ == "__main__":
    for n in sys.argv[1:]:
        main(n)
