# -*- coding: utf-8 -*-
"""診斷：單一 chunk 對多個記文檔的 4-gram 最佳視窗重疊率。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from align_lib import ROOT, NoteIndex, grams, norm, read_lines  # noqa: E402


def paras_of(path):
    out = []
    for i, l in enumerate(read_lines(path)):
        if l.startswith("\u3000\u3000"):
            out.append((i + 1, l[2:].strip()))
        elif l.strip() and not l.startswith(("底本", "（節自", "====")):
            out.append((i + 1, l.strip()))
    return out


def main():
    book, chunk, *notes = sys.argv[1:]
    src = os.path.join(ROOT, "TXT_分卷", book, chunk + ".txt")
    ps = paras_of(src)
    print(f"### {book}/{chunk}  段數={len(ps)}")
    idxs = []
    for nf in notes:
        idxs.append((nf, NoteIndex(os.path.join(ROOT, "TXT", "資持記", nf + ".txt"))))
    for k, (ln, text) in enumerate(ps, 1):
        g = grams(norm(text))
        row = [f"{k:3d} L{ln:3d} len={len(text):4d} ng={len(g):4d} | {text[:18]}"]
        for nf, idx in idxs:
            if not g:
                continue
            W = max(240, 3 * len(text))
            cov, a, b, _ = idx.best_window(g, W)
            r = cov / len(g)
            l1, l2 = idx.span_lines(a, b)
            snip = "".join(idx.norm_chars[a:a + 24])
            row.append(f"   {nf}: cov={cov:4d}/{len(g):4d}={r:.2f} lines={l1}-{l2} span={b-a:5d} | {snip}")
        print("\n".join(row))


if __name__ == "__main__":
    main()
