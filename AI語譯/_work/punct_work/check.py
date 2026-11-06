import json, os, glob, difflib, sys, io

base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work"
work = os.path.join(base, "punct_work")

MARKS = "\uff0c\u3002\u3001\uff1b\uff1a\uff1f\uff01\u300c\u300d\uff08\uff09"
MSET = set(MARKS)

def strip_marks(s):
    return "".join(c for c in s if c not in MSET)

inp = json.load(open(os.path.join(base, "ys_punct_in.json"), encoding="utf-8"))
keys = list(inp.keys())

outs = {}
errs = []
for f in sorted(glob.glob(os.path.join(work, "p*.txt"))):
    for ln, line in enumerate(open(f, encoding="utf-8"), 1):
        line = line.rstrip("\n")
        if not line.strip():
            continue
        if "\t" not in line:
            errs.append(f"{os.path.basename(f)}:{ln} no TAB")
            continue
        idx, text = line.split("\t", 1)
        try:
            b, p = idx.strip().split(".")
            k = (int(b), int(p))
        except Exception:
            errs.append(f"{os.path.basename(f)}:{ln} bad idx {idx!r}")
            continue
        if k in outs:
            errs.append(f"duplicate {idx}")
        outs[k] = text

report = []
bad = 0
missing = 0
total_changed = 0
total_marks = 0
for bi, key in enumerate(keys):
    paras = inp[key]
    for pi, src in enumerate(paras):
        k = (bi, pi)
        if k not in outs:
            missing += 1
            continue
        got = outs[k]
        a = strip_marks(src)
        b = strip_marks(got)
        if a == b:
            if got != src:
                total_changed += 1
            total_marks += sum(1 for c in got if c in MSET) - sum(1 for c in src if c in MSET)
            continue
        bad += 1
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        segs = []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != "equal":
                segs.append(f"[{tag}] exp={a[max(0,i1-8):i2+8]!r} got={b[max(0,j1-8):j2+8]!r}")
        report.append(f"=== {bi}.{pi} (len src={len(a)} out={len(b)})")
        for s in segs[:8]:
            report.append("   " + s)

allok = (bad == 0 and missing == 0 and not errs)
head = []
head.append(f"files={len(glob.glob(os.path.join(work,'p*.txt')))} filled={len(outs)} expected={sum(len(v) for v in inp.values())}")
head.append(f"mismatch={bad} missing={missing} parse_errors={len(errs)} changed={total_changed} marks_added={total_marks}")
if errs:
    head.append("PARSE ERRORS:")
    head.extend("  " + e for e in errs)
head.extend(report)

if allok:
    blocks = []
    for bi, key in enumerate(keys):
        texts = [outs[(bi, pi)] for pi in range(len(inp[key]))]
        blocks.append({"key": key, "texts": texts})
    with open(os.path.join(base, "ys_punct_out.json"), "w", encoding="utf-8") as fh:
        json.dump({"blocks": blocks}, fh, ensure_ascii=False, indent=1)
    head.append("WROTE ys_punct_out.json")
else:
    head.append("NOT WRITTEN")

open(os.path.join(work, "report.txt"), "w", encoding="utf-8").write("\n".join(head))
print("ok" if allok else "issues")
