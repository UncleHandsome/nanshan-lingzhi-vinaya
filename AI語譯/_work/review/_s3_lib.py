# -*- coding: utf-8 -*-
"""Helper: normalized texts (資持記, 行事鈔, current translations) + search with context."""
import io, os, re, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"

def read_raw(p):
    with io.open(p, encoding="utf-8-sig") as f:
        return f.read()

def norm(p):
    t = read_raw(p)
    t = t.replace("\r", "").replace("\n", "")
    return t

_cache = {}
def zhichi():
    if "z" not in _cache:
        _cache["z"] = norm(os.path.join(ROOT, "_src", "_src_資持記.txt"))
    return _cache["z"]

def chaos():
    if "c" not in _cache:
        _cache["c"] = norm(os.path.join(ROOT, "TXT", "01_四分律刪繁補闕行事鈔.txt"))
    return _cache["c"]

def find(text, needle, ctx=180, limit=8):
    out = []
    i = 0
    while True:
        j = text.find(needle, i)
        if j < 0:
            break
        a = max(0, j - ctx); b = min(len(text), j + len(needle) + ctx)
        out.append(text[a:b])
        i = j + 1
        if len(out) >= limit:
            break
    return out

if __name__ == "__main__":
    args = sys.argv[1:]
    src = args[0] if args else "z"
    for needle in args[1:]:
        text = zhichi() if src == "z" else chaos()
        print("=" * 20, needle, "in", src, "count=", text.count(needle))
        for s in find(text, needle):
            print(s)
            print("-" * 8)
