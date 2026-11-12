# -*- coding: utf-8 -*-
"""Analyze 存疑材料/待套用_re0.tsv against current chunk paragraphs (read-only)."""
import csv, difflib, io, os, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
TSV = os.path.join(ROOT, "存疑材料", "待套用_re0.tsv")
OUTDIR = os.path.join(ROOT, "AI語譯", "out", "03_業疏")

def load_rows():
    with open(TSV, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f, delimiter="\t"))
    header = rows[0]
    return header, rows[1:]

def read_text(path):
    with open(path, "rb") as f:
        raw = f.read()
    # detect newline
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    nl = "\r\n" if crlf >= lf else "\n"
    return raw.decode("utf-8"), nl

def main():
    header, rows = load_rows()
    print("HEADER:", header)
    print("ROWS:", len(rows))
    cache = {}
    for idx, r in enumerate(rows, 1):
        if len(r) < 5:
            print("!! row", idx, "too few cols", len(r)); continue
        segid, book, chunk, para, newp = r[0], r[1], r[2], r[3], r[4]
        reason = r[5] if len(r) > 5 else ""
        # locate file
        cand = [fn for fn in os.listdir(OUTDIR) if fn.endswith(".txt") and fn.startswith(chunk + "_")]
        if len(cand) != 1:
            print("!! cannot resolve chunk", chunk, cand); continue
        path = os.path.join(OUTDIR, cand[0])
        if path not in cache:
            txt, nl = read_text(path)
            parts = txt.split(nl + nl)
            cache[path] = (txt, nl, parts)
        txt, nl, parts = cache[path]
        pidx = int(para)
        cur = parts[pidx - 1] if 0 < pidx <= len(parts) else None
        print("=" * 100)
        print(f"[{idx}] {segid} {book}/{cand[0]} #{para}  parts={len(parts)}")
        if cur is None:
            print("  !! paragraph index out of range"); continue
        print("  CUR LEN:", len(cur), " NEW LEN:", len(newp))
        print("  CUR:", cur[:2000])
        print("  NEW:", newp[:2000])
        same = cur == newp
        print("  EQUAL:", same)
        if not same:
            sm = difflib.SequenceMatcher(None, cur, newp, autojunk=False)
            print("  RATIO: %.4f" % sm.ratio())
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                if tag == "equal":
                    continue
                print(f"   {tag}: CUR[{i1}:{i2}]={cur[i1:i2]!r}")
                print(f"          NEW[{j1}:{j2}]={newp[j1:j2]!r}")

if __name__ == "__main__":
    main()
