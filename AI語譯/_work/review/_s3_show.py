# -*- coding: utf-8 -*-
"""Show material segments for a doc, or a specific seg."""
import io, json, os, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
rows = json.load(io.open(os.path.join(ROOT, "AI語譯", "_work", "review", "_s3_rows.json"), encoding="utf-8"))

def show(doc, src_only=False):
    for r in rows:
        if r["doc"] != doc:
            continue
        print("【%03d-%04d】%s" % (r["doc"], r["seg"], r["ref"]))
        print("原：" + r["src"])
        if not src_only:
            print("譯：" + r["cur"])
        print()

if __name__ == "__main__":
    if sys.argv[1] == "src":
        for d in sys.argv[2:]:
            show(int(d), True)
    else:
        for d in sys.argv[1:]:
            show(int(d))
