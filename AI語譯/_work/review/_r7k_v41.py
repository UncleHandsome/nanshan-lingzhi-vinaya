# -*- coding: utf-8 -*-
"""7K 03_業疏 卷四之一 校閱 helper."""
import io, json, os, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT, "AI語譯", "out", "03_業疏")
SRC = os.path.join(ROOT, "TXT_分卷_標點", "03_業疏")


def load_paras(book_file, base=OUT):
    """Return list of (line_no, text) for non-empty lines, 1-based paragraph idx."""
    p = os.path.join(base, book_file)
    with io.open(p, encoding="utf-8", newline="") as f:
        raw = f.read()
    # split keeping structure
    lines = raw.split("\n")
    paras = []
    for i, ln in enumerate(lines):
        t = ln.rstrip("\r")
        if t.strip():
            paras.append((i, t))
    return paras


def show(book_file, idxs, base=OUT):
    paras = load_paras(book_file, base)
    for n in idxs:
        i, t = paras[n - 1]
        print("--- #%d (line %d) ---" % (n, i + 1))
        print(t)


def apply_edits(book_file, edits, base=OUT):
    """edits: list of dict(idx=1based, new=...) or dict(idx, old, new)."""
    p = os.path.join(base, book_file)
    with io.open(p, encoding="utf-8", newline="") as f:
        raw = f.read()
    nl = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split("\n")
    paras = []
    for i, ln in enumerate(lines):
        if ln.rstrip("\r").strip():
            paras.append(i)
    done = 0
    for e in edits:
        i = paras[e["idx"] - 1]
        cur = lines[i].rstrip("\r")
        if "old" in e and cur != e["old"]:
            raise SystemExit("MISMATCH #%d\nOLD: %r\nCUR: %r" % (e["idx"], e["old"], cur))
        if cur == e["new"]:
            continue
        lines[i] = e["new"] + ("\r" if lines[i].endswith("\r") else "")
        done += 1
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lines))
    return done


def diff_paras(book_file, base_a, base_b):
    a = load_paras(book_file, base_a)
    b = load_paras(book_file, base_b)
    if len(a) != len(b):
        print("COUNT DIFF", len(a), len(b))
    n = 0
    for k in range(min(len(a), len(b))):
        if a[k][1] != b[k][1]:
            n += 1
            print("#%d\n A:%s\n B:%s" % (k + 1, a[k][1], b[k][1]))
    print("diffs:", n)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "show":
        show(sys.argv[2], [int(x) for x in sys.argv[3:]])
    elif cmd == "apply":
        book = sys.argv[2]
        edits = json.load(io.open(sys.argv[3], encoding="utf-8"))
        print("edited:", apply_edits(book, edits))
