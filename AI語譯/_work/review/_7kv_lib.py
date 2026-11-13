# -*- coding: utf-8 -*-
"""7K 卷派工（卷中之二）共用工具：解析校閱材料、讀寫 chunk、備份、驗證。"""
import io, os, re, json, shutil, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
BOOK = "01_行事鈔"
OUTDIR = os.path.join(ROOT, "AI語譯", "out", BOOK)
BAKDIR = os.path.join(ROOT, "歸檔", "7K卷修正前", BOOK)

LABEL_RE = re.compile(r"^【(\d{3,4})-(\d{4})】(\S+?)/([^#]+)#(\d+)$")


def read_text(path):
    b = open(path, "rb").read()
    return b, b.decode("utf-8")


def para_index_map(text):
    """回傳 list，元素為 (line_index, content_without_eol)，只含非空行。"""
    lines = text.split("\n")
    out = []
    for i, ln in enumerate(lines):
        c = ln.rstrip("\r")
        if c.strip():
            out.append((i, c))
    return out


def load_chunk(chunk):
    p = os.path.join(OUTDIR, chunk + ".txt")
    b, t = read_text(p)
    return p, b, t


def chunk_paras(chunk):
    p, b, t = load_chunk(chunk)
    return p, b, t, para_index_map(t)


def parse_material(nnn):
    """解析 校閱_7K/校閱_NNN.txt → list of dict(label, nnn, num, chunk, seg, src, tr)"""
    p = os.path.join(ROOT, "校閱_7K", "校閱_%s.txt" % nnn)
    _, t = read_text(p)
    lines = t.split("\n")
    items = []
    cur = None
    for ln in lines:
        c = ln.rstrip("\r")
        m = LABEL_RE.match(c)
        if m:
            if cur:
                items.append(cur)
            cur = dict(label=m.group(1) + "-" + m.group(2), nnn=int(m.group(1)), num=int(m.group(2)),
                       chunk=m.group(4), seg=int(m.group(5)), src="", tr="")
            continue
        if cur is None:
            continue
        if c.startswith("【原文】"):
            cur["src"] = c[len("【原文】"):]
        elif c.startswith("【譯文】"):
            cur["tr"] = c[len("【譯文】"):]
        elif c.strip() == "":
            pass
        else:
            if cur["tr"]:
                cur["tr"] += c
            elif cur["src"]:
                cur["src"] += c
    if cur:
        items.append(cur)
    return items


def eol_of(t):
    crlf = t.count("\r\n")
    lf = len(re.findall(r"(?<!\r)\n", t))
    return "CRLF" if crlf > lf else "LF"


def save_chunk(chunk, text):
    p = os.path.join(OUTDIR, chunk + ".txt")
    with open(p, "wb") as f:
        f.write(text.encode("utf-8"))
    return p


def backup(chunk, suffix="v"):
    src = os.path.join(OUTDIR, chunk + ".txt")
    if not os.path.isdir(BAKDIR):
        os.makedirs(BAKDIR)
    dst = os.path.join(BAKDIR, "%s_%s.txt" % (chunk, suffix))
    shutil.copy2(src, dst)
    return dst
