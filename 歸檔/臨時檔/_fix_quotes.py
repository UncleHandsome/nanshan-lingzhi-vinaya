# -*- coding: utf-8 -*-
"""從材料取回報告【原文】【譯文】欄的逐字原形。
只處理「折平標點寬度後完全相符」者（含節引），其餘一律不动並點名。
用法：python _fix_quotes.py 30 65 [--apply]
"""
import os, re, sys, json, collections

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "\u6821\u95b1\u6279\u6b21")
SL = os.path.join(SRC, "_\u5207\u7247")
PARTS = os.path.join(SRC, "\u6821\u95b1\u7d50\u679c", "parts")
L_SRC = "\u3010\u539f\u6587\u3011"
L_TR = "\u3010\u8b6f\u6587\u3011"
SEG = re.compile(r"^\u3010(\d{2}-\d{4})\u3011(.*)$")
HEAD = re.compile(r"^###\s*(\d{2}-\d{4})\s*\uff5c")
FIELDS = {"\u539f\u6587\uff1a": "src", "\u8b6f\u6587\uff1a": "tr"}

WIDE = "\uff0c\uff1b\uff1a\u3002\uff01\uff1f\uff08\uff09"
NARROW = ",;:.!?()"
FOLD = {}
for a, b in zip(WIDE, NARROW):
    FOLD[a] = b
    FOLD[b] = b


def fold(s):
    return "".join(FOLD.get(c, c) for c in s if not c.isspace())


def parse_slice(path):
    out, cur = {}, None
    for line in open(path, encoding="utf-8").read().split("\n"):
        m = SEG.match(line)
        if m:
            cur = m.group(1)
            out[cur] = {"src": "", "tr": ""}
        elif cur and line.startswith(L_SRC):
            out[cur]["src"] += line[len(L_SRC):]
        elif cur and line.startswith(L_TR):
            out[cur]["tr"] += line[len(L_TR):]
    return out


def main():
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    apply = "--apply" in sys.argv
    d = json.load(open(os.path.join(SL, "index.json"), encoding="utf-8"))
    n_fix = n_skip = n_ok = 0
    touched = []
    for x in d:
        if not (lo <= int(x["stem"]) <= hi):
            continue
        for p in x["parts"]:
            rp = os.path.join(PARTS, p["report"])
            if not os.path.exists(rp):
                continue
            mat = parse_slice(os.path.join(SL, p["slice"]))
            lines = open(rp, encoding="utf-8").read().split("\n")
            cur = None
            changed = 0
            for i, line in enumerate(lines):
                m = HEAD.match(line)
                if m:
                    cur = m.group(1)
                    continue
                if line.startswith("###"):
                    cur = None
                    continue
                if cur is None or not line.startswith("- "):
                    continue
                body = line[2:]
                hit = None
                for f, k in FIELDS.items():
                    if body.startswith(f):
                        hit = (f, k)
                        break
                if hit is None:
                    continue
                f, k = hit
                if cur not in mat:
                    continue
                quoted = body[len(f):]
                exact = mat[cur][k].strip()
                if fold(quoted) == fold(exact):
                    if quoted != exact:
                        lines[i] = "- " + f + exact
                        changed += 1
                    else:
                        n_ok += 1
                    continue
                fq = fold(quoted)
                chars, idx = [], []
                for j, c in enumerate(exact):
                    if not c.isspace():
                        chars.append(c)
                        idx.append(j)
                fe = "".join(FOLD.get(c, c) for c in chars)
                pos = fe.find(fq) if fq else -1
                if pos >= 0:
                    piece = exact[idx[pos]:idx[pos + len(fq) - 1] + 1]
                    if quoted != piece:
                        lines[i] = "- " + f + piece
                        changed += 1
                    else:
                        n_ok += 1
                    continue
                n_skip += 1
                print("SKIP %s %s %s" % (p["name"], cur, f[:2]))
            if changed:
                n_fix += changed
                touched.append((p["name"], changed))
                if apply:
                    open(rp, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    print()
    print("%s\uff1a\u53ef\u9084\u539f\u6b04\u4f4d %d\uff08%d \u6a94\uff09\uff1b\u5df2\u9010\u5b57 %d\uff1b\u7121\u6cd5\u9084\u539f %d"
          % ("APPLY" if apply else "DRYRUN", n_fix, len(touched), n_ok, n_skip))
    for name, c in touched:
        print("  %-10s %d" % (name, c))
    return 0


if __name__ == "__main__":
    sys.exit(main())