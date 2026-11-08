# -*- coding: utf-8 -*-
"""量 parts/ 報告本身：管轄、標題、引文逐字、統計對帳。用法 python _chk_parts.py 30 65"""
import os, re, sys, json, collections

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "\u6821\u95b1\u6279\u6b21")
SL = os.path.join(SRC, "_\u5207\u7247")
PARTS = os.path.join(SRC, "\u6821\u95b1\u7d50\u679c", "parts")

L_SRC = "\u3010\u539f\u6587\u3011"
L_TR = "\u3010\u8b6f\u6587\u3011"
F_SRC = "\u539f\u6587\uff1a"
F_TR = "\u8b6f\u6587\uff1a"
F_ALL = ["\u539f\u6587\uff1a", "\u8b6f\u6587\uff1a", "\u554f\u984c\uff1a",
         "\u4f9d\u64da\uff1a", "\u5efa\u8b70\uff1a", "\u4fe1\u5fc3\uff1a"]
DOUBT = "\u5b58\u7591"
CHKED = "\u5df2\u6aa2\u67e5"

SEG = re.compile(r"^\u3010(\d{2}-\d{4})\u3011(.*)$")
HEAD = re.compile(r"^###\s*(\d{2}-\d{4})\s*\uff5c\s*(.*?)\s*\uff5c\s*(P[012])\s*\uff5c\s*(.*)$")
STAT = re.compile(CHKED + r"\s*(\d+)\s*\u6bb5\s*[;\uff1b]\s*P0\s*(\d+)\s*\u3001\s*P1\s*(\d+)\s*\u3001\s*P2\s*(\d+)\s*[;\uff1b]\s*" + DOUBT + r"\s*(\d+)\s*\u689d")
STAT2 = re.compile(CHKED + r"\s*(\d+)\s*\u6bb5")
DBT = re.compile(r"^-\s*(\d{2}-\d{4})\s*\uff1a", re.M)


def nows(s):
    return re.sub(r"\s+", "", s)


def parse_slice(path):
    out = {}
    cur = None
    for line in open(path, encoding="utf-8").read().split("\n"):
        m = SEG.match(line)
        if m:
            cur = m.group(1)
            out[cur] = {"tag": m.group(2), "src": "", "tr": ""}
        elif cur and line.startswith(L_SRC):
            out[cur]["src"] += line[len(L_SRC):]
        elif cur and line.startswith(L_TR):
            out[cur]["tr"] += line[len(L_TR):]
    return out


def parse_report(path):
    txt = open(path, encoding="utf-8").read()
    items = []
    cur = None
    for line in txt.split("\n"):
        m = HEAD.match(line)
        if m:
            cur = {"id": m.group(1), "tag": m.group(2), "p": m.group(3),
                   "kind": m.group(4), "fields": {}}
            items.append(cur)
            continue
        if line.startswith("###"):
            cur = {"id": "?", "tag": line[3:].strip(), "p": "?",
                   "kind": "", "fields": {}, "malformed": True}
            items.append(cur)
            continue
        if cur is not None and line.startswith("- "):
            body = line[2:]
            for f in F_ALL:
                if body.startswith(f):
                    cur["fields"][f] = body[len(f):]
                    cur["last"] = f
                    break
        elif cur is not None and line.strip() and cur.get("last") and not line.startswith("#"):
            cur["fields"][cur["last"]] += line
    doubts = [m.group(1) for m in DBT.finditer(txt)]
    st = STAT.search(txt)
    st2 = STAT2.search(txt)
    return txt, items, doubts, st, st2


def main():
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    only_bad = "--bad" in sys.argv
    d = json.load(open(os.path.join(SL, "index.json"), encoding="utf-8"))
    n_done = n_seg = 0
    tot = collections.Counter()
    problems = []
    for x in d:
        if not (lo <= int(x["stem"]) <= hi):
            continue
        for p in x["parts"]:
            rp = os.path.join(PARTS, p["report"])
            if not os.path.exists(rp):
                problems.append((p["name"], "MISSING", "\u5831\u544a\u4e0d\u5b58\u5728"))
                continue
            mat = parse_slice(os.path.join(SL, p["slice"]))
            txt, items, doubts, st, st2 = parse_report(rp)
            if st2 is None:
                problems.append((p["name"], "NOSTAT", "\u7121\u7d71\u8a08\u884c"))
                continue
            n_done += 1
            n_seg += int(st2.group(1))
            err = []
            note = []
            if int(st2.group(1)) != p["segs"]:
                err.append("\u7d71\u8a08\u6bb5\u6578 %s != \u5be6\u969b %d" % (st2.group(1), p["segs"]))
            if len(mat) != p["segs"]:
                err.append("\u6750\u6599\u89e3\u6790 %d != index %d" % (len(mat), p["segs"]))
            cnt = collections.Counter()
            for it in items:
                if it.get("malformed") or it["id"] == "?":
                    err.append("\u6a19\u984c\u4e0d\u5408\u5f0f\uff1a" + it["tag"][:40])
                    continue
                sid = it["id"]
                cnt[it["p"]] += 1
                tot[it["p"]] += 1
                if sid not in mat:
                    err.append("\u7de8\u865f\u4e0d\u5728\u672c\u7247\uff1a" + sid)
                    continue
                if sid not in p["ids"]:
                    err.append("\u7de8\u865f\u4e0d\u5728 index \u540d\u55ae\uff1a" + sid)
                if nows(it["tag"]) != nows(mat[sid]["tag"]):
                    err.append("\u6a19\u7c64\u4e0d\u7b26\uff1a" + sid)
                for f, key in ((F_SRC, "src"), (F_TR, "tr")):
                    q = it["fields"].get(f)
                    if q is None:
                        err.append("\u7f3a\u6b04\u4f4d %s\uff1a%s" % (f[:2], sid))
                        continue
                    a, b = nows(q), nows(mat[sid][key])
                    if a == b:
                        continue
                    if a and a in b:
                        note.append("\u7bc0\u5f15 %s\uff1a%s" % (f[:2], sid))
                    else:
                        err.append("\u975e\u9010\u5b57 %s\uff1a%s" % (f[:2], sid))
                if it["p"] == "P0" and not it["fields"].get("\u4f9d\u64da\uff1a", "").strip():
                    err.append("P0 \u7121\u4f9d\u64da\uff1a" + sid)
            tot["\u5b58\u7591"] += len(doubts)
            if st:
                exp = (int(st.group(2)), int(st.group(3)), int(st.group(4)), int(st.group(5)))
                got = (cnt["P0"], cnt["P1"], cnt["P2"], len(doubts))
                if exp != got:
                    err.append("\u7d71\u8a08\u4e0d\u5c0d\u5e33 \u5ba3\u7a31%s \u5be6\u6578%s" % (exp, got))
            else:
                err.append("\u7d71\u8a08\u884c\u683c\u5f0f\u4e0d\u5408\u56b4\u683c\u6a23\u5f0f")
            if note:
                tot["\u7bc0\u5f15"] += len(note)
            if err:
                problems.append((p["name"], "FAIL", err))
            elif not only_bad:
                print("OK   %-10s segs=%-4d items=%-3d P0=%d P1=%d P2=%d \u5b58\u7591=%d%s"
                      % (p["name"], p["segs"], len(items), cnt["P0"], cnt["P1"], cnt["P2"], len(doubts),
                         ("  \u7bc0\u5f15 %d" % len(note)) if note else ""))
    print()
    print("\u5df2\u5b8c\u6210\u7247 %d\uff1b\u5ba3\u7a31\u5df2\u6aa2\u67e5\u6bb5\u6578 %d" % (n_done, n_seg))
    print("\u5be6\u6578\u610f\u898b P0=%d P1=%d P2=%d\uff1b\u5b58\u7591 %d\uff1b\u7bc0\u5f15\u6b04\u4f4d %d"
          % (tot["P0"], tot["P1"], tot["P2"], tot["\u5b58\u7591"], tot["\u7bc0\u5f15"]))
    print("\u7570\u5e38\u7247 %d" % len(problems))
    for name, kind, err in problems:
        if isinstance(err, list):
            print("FAIL %-10s (%d)" % (name, len(err)))
            for e in err[:12]:
                print("     " + e)
            if len(err) > 12:
                print("     ...\u5171 %d \u689d" % len(err))
        else:
            print("%s %-10s %s" % (kind, name, err))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())