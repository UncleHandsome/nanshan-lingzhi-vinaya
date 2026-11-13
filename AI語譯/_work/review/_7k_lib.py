# -*- coding: utf-8 -*-
"""7K 擋檔處理共用工具：解析校閱材料、讀寫 chunk、備份、驗證。"""
import io, os, re, json, shutil, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
BOOK = "02_戒疏"
OUTDIR = os.path.join(ROOT, "AI語譯", "out", BOOK)
BAKDIR = os.path.join(ROOT, "歸檔", "7K擋檔修正前", BOOK)

LABEL_RE = re.compile(r"^【(\d{3,4})-(\d{4})】(\S+?)/([^#]+)#(\d+)$")


def read_text(path):
    b = open(path, "rb").read()
    return b, b.decode("utf-8")


def split_paras(text):
    """回傳 (lines, paras)；lines 保留原行尾，paras 為非空段落（去行尾）。"""
    raw = text.split("\n")
    return raw


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


def parse_material(nnn):
    """解析 校閱_7K/校閱_NNN.txt → list of dict(label, seq, chunk, seg, src, tr)"""
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
            cur = dict(label=m.group(1) + "-" + m.group(2), seq=m.group(1) + "-" + m.group(2),
                       nnn=int(m.group(1)), num=int(m.group(2)), chunk=m.group(4), seg=int(m.group(5)),
                       src="", tr="")
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
            # 續行（材料罕見換行）
            if cur["tr"]:
                cur["tr"] += c
            elif cur["src"]:
                cur["src"] += c
    if cur:
        items.append(cur)
    return items


def chunk_paras(chunk):
    p, b, t = load_chunk(chunk)
    return p, b, t, para_index_map(t)


def main():
    nnn = sys.argv[1]
    items = parse_material(nnn)
    chunks = {}
    print("file", nnn, "items", len(items))
    for it in items:
        ch = it["chunk"]
        if ch not in chunks:
            p, b, t, pm = chunk_paras(ch)
            chunks[ch] = (p, b, t, pm)
            crlf = t.count("\r\n")
            lf = len(re.findall(r"(?<!\r)\n", t))
            print("  chunk", ch, "bytes", len(b), "paras", len(pm), "CRLF", crlf, "bareLF", lf,
                  "blank_lines_ok", all(not t.split("\n")[i].strip() for i in range(1, len(t.split("\n")) - 1, 2)))
        p, b, t, pm = chunks[ch]
        idx = it["seg"] - 1
        if idx >= len(pm):
            print("  MISSING seg", it["seg"], it["label"], "paras", len(pm))
            continue
        cur = pm[idx][1]
        same = (cur.strip() == it["tr"].strip())
        print("  %s #%d %s" % (it["label"], it["seg"], "OK" if same else "DIFF"))
        if not same:
            print("    material:", it["tr"][:150])
            print("    current :", cur[:150])


if __name__ == "__main__":
    main()
