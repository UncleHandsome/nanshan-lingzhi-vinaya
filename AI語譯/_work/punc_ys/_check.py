import json, os

src = json.load(open(r"AI語譯/_work/punc_ys/04.json", encoding="utf-8"))["items"]
out = json.load(open(r"AI語譯/_work/punc_ys/out_04.json", encoding="utf-8"))

PUNC = "，。、；：？！「」"
errs = []
if not isinstance(out, list):
    errs.append("not a list")
if len(out) != len(src):
    errs.append("count %d vs %d" % (len(out), len(src)))
for i, (a, b) in enumerate(zip(src, out)):
    if set(b.keys()) != {"file", "line", "text"}:
        errs.append("%d keys %s" % (i, sorted(b.keys())))
    if a["file"] != b["file"]:
        errs.append("%d file" % i)
    if a["line"] != b["line"] or not isinstance(b["line"], int):
        errs.append("%d line" % i)
    if "".join(c for c in a["text"] if c not in PUNC) != "".join(c for c in b["text"] if c not in PUNC):
        errs.append("%d char mismatch" % i)
    if not (b["text"].endswith("。") or b["text"].endswith("。」")):
        errs.append("%d no final period" % i)

print("items=%d errors=%d" % (len(out), len(errs)))
for e in errs:
    print("ERR", e)
print("bytes=%d" % os.path.getsize(r"AI語譯/_work/punc_ys/out_04.json"))
