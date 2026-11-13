# -*- coding: utf-8 -*-
"""套用 _7kv_edits.json 的修訂：先備份，逐段精確替換（old 在該段須恰出現一次）。
成功套用者標記 done=true，重跑時只處理未 done 者。"""
import os, sys, json, io, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _7kv_lib as L

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "_7kv_edits.json")


def load_spec():
    if not os.path.exists(SPEC):
        return []
    return json.load(open(SPEC, encoding="utf-8"))


def save_spec(spec):
    json.dump(spec, open(SPEC, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def apply_all(spec, dry=False):
    pending = [e for e in spec if not e.get("done")]
    chunks = sorted(set(e["chunk"] for e in pending))
    for ch in chunks:
        dst = os.path.join(L.BAKDIR, ch + "_v.txt")
        if not os.path.exists(dst):
            os.makedirs(L.BAKDIR, exist_ok=True)
            shutil.copy2(os.path.join(L.OUTDIR, ch + ".txt"), dst)
            print("backup", ch, "->", dst)
        else:
            print("backup exists", dst)

    by_chunk = {}
    for e in pending:
        by_chunk.setdefault(e["chunk"], []).append(e)
    ok = True
    for ch, edits in by_chunk.items():
        p = os.path.join(L.OUTDIR, ch + ".txt")
        raw = io.open(p, encoding="utf-8", newline="").read()
        lines = raw.split("\n")
        for e in edits:
            seg = e["seg"]
            cnt = 0
            li = -1
            for i, ln in enumerate(lines):
                if ln.strip():
                    cnt += 1
                    if cnt == seg:
                        li = i
                        break
            if li < 0:
                print("!! seg not found", ch, seg)
                ok = False
                continue
            cur = lines[li]
            eol = ""
            if cur.endswith("\r"):
                cur, eol = cur[:-1], "\r"
            n = cur.count(e["old"])
            if n != 1:
                print("!! old count=%d in %s#%d: %r" % (n, ch, seg, e["old"][:70]))
                ok = False
                continue
            lines[li] = cur.replace(e["old"], e["new"], 1) + eol
            e["done"] = True
            print("OK %s#%d  %r -> %r" % (ch, seg, e["old"][:36], e["new"][:36]))
        if not dry:
            io.open(p, "w", encoding="utf-8", newline="").write("\n".join(lines))
    if not dry:
        save_spec(spec)
    return ok


if __name__ == "__main__":
    spec = load_spec()
    print("total", len(spec), "pending", len([e for e in spec if not e.get("done")]))
    ok = apply_all(spec, dry=("--dry" in sys.argv))
    print("ALL OK" if ok else "HAS FAILURES")
