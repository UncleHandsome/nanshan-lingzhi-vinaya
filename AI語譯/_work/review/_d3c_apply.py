# -*- coding: utf-8 -*-
"""Apply 7K 資持記 下三_c edits.

JSON: {"1989": {"chunk": "15e_下三", "edits": [{"out":27,"old":"...","new":"...","cat":"義理","why":"..."}]}}
`out` = 該 chunk 第 out 個非空段落（現行 out 檔，非校閱材料 idx）。
"""
import os, sys, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _d3c_lib as L

BAK = os.path.join(L.ROOT, "歸檔", "7K卷修正前", "資持記")
LOG = os.path.join(L.ROOT, "AI語譯", "_work", "review", "_d3c_log.jsonl")


def backup(chunk):
    os.makedirs(BAK, exist_ok=True)
    dst = os.path.join(BAK, chunk + "_v.txt")
    if not os.path.exists(dst):
        shutil.copyfile(os.path.join(L.OUT, chunk + ".txt"), dst)
        return dst
    return None


def apply(spec_path):
    spec = json.load(open(spec_path, encoding="utf-8"))
    bychunk = {}
    for n in sorted(spec):
        for e in spec[n]["edits"]:
            bychunk.setdefault(spec[n]["chunk"], []).append((n, e))
    log = []
    for chunk, edits in bychunk.items():
        lines, eol = L.read_out(chunk)
        before = sum(1 for l in lines if l.strip())
        ne = [i for i, l in enumerate(lines) if l.strip()]
        for n, e in edits:
            ln = ne[e["out"] - 1]
            cur = lines[ln]
            c = cur.count(e["old"])
            if c != 1:
                raise SystemExit("檔%s OUT#%d old count=%d\n%r" % (n, e["out"], c, e["old"]))
            lines[ln] = cur.replace(e["old"], e["new"])
            log.append(dict(n=int(n), chunk=chunk, out=e["out"], cat=e.get("cat", ""),
                            old=e["old"], new=e["new"], why=e.get("why", "")))
        after = sum(1 for l in lines if l.strip())
        if before != after:
            raise SystemExit("段數變動 %s %d->%d" % (chunk, before, after))
        backup(chunk)
        out = os.path.join(L.OUT, chunk + ".txt")
        with open(out, "w", encoding="utf-8", newline="") as f:
            f.write(eol.join(lines) + eol)
        print("WROTE", chunk, len(edits), "nonempty", after)
    with open(LOG, "a", encoding="utf-8") as f:
        for r in log:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("EDITS", len(log))


if __name__ == "__main__":
    apply(sys.argv[1])
