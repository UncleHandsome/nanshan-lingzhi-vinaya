# -*- coding: utf-8 -*-
"""Find per-chunk offset: material 譯文 vs out paragraphs."""
import io, os, re, json

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
MAT = os.path.join(ROOT, "校閱_10K")
OUTD = os.path.join(ROOT, "AI語譯", "out")
BOOKS = ("03_業疏", "04_比丘尼鈔", "05_拾毗尼義鈔")


def paras(book, chunk):
    p = os.path.join(OUTD, book, chunk + ".txt")
    t = io.open(p, encoding="utf-8", newline="").read().replace("\r\n", "\n")
    ps = t.split("\n\n")
    if ps and ps[-1].endswith("\n"):
        ps[-1] = ps[-1][:-1]
    return ps


def main():
    # collect material translations per (book, chunk, seg)
    tr = {}
    for fn in sorted(os.listdir(MAT)):
        n = int(re.sub(r"\D", "", fn))
        if n < 1393:
            continue
        t = io.open(os.path.join(MAT, fn), encoding="utf-8").read()
        for b in re.split(r"(?=【\d{4}-\d{4}】)", t):
            m = re.match(r"【(\d{4}-\d{4})】([^\r\n/]+)/([^#\r\n]+)#(\d+)", b)
            if not m:
                continue
            book, chunk, seg = m.group(2).strip(), m.group(3).strip(), int(m.group(4))
            if book not in BOOKS:
                continue
            mt = re.search(r"【譯文】(.*)", b, re.S)
            if mt:
                tr.setdefault((book, chunk), {})[seg] = mt.group(1).strip()
    report = {}
    for (book, chunk), segs in sorted(tr.items()):
        ps = paras(book, chunk)
        votes = {}
        det = []
        for seg in sorted(segs)[:6]:
            txt = segs[seg]
            key = re.sub(r"\s", "", txt)[:40]
            hit = None
            for i, p in enumerate(ps):
                if re.sub(r"\s", "", p).startswith(key[:25]):
                    hit = i
                    break
            det.append((seg, hit))
            if hit is not None:
                votes[hit - seg + 1] = votes.get(hit - seg + 1, 0) + 1
        best = max(votes, key=votes.get) if votes else None
        report.setdefault(book, {})[chunk] = {"offset": best, "n": len(segs), "paras": len(ps), "det": det}
        if best != 0:
            print(book, chunk, "n=%d paras=%d offset=%s" % (len(segs), len(ps), best), det)
    json.dump(report, io.open(os.path.join(ROOT, "AI語譯", "_work", "review", "_r2o_off.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    bad = [(b, c, d["offset"]) for b in report for c, d in report[b].items() if d["offset"] != 0]
    print("chunks with offset!=0:", len(bad), bad[:10])
    print("chunks total:", sum(len(report[b]) for b in report))


if __name__ == "__main__":
    main()
