# -*- coding: utf-8 -*-
"""7K 卷三之六 套用：以段落索引整段替換 out/<chunk>.txt
用法: python _r7k6_apply.py spec.json
spec: {"file":"AI語譯/out/03_業疏/17a_卷三之六.txt",
       "backup":"歸檔/7K卷修正前/03_業疏/17a_卷三之六_v.txt",
       "edits":[{"i":2,"prefix":"在五戒的正明中","new":"..."}]}
"""
import io, os, sys, json, shutil

base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"

def main(spec_path):
    spec = json.load(io.open(spec_path, encoding="utf-8"))
    fp = os.path.join(base, spec["file"])
    bk = os.path.join(base, spec["backup"])
    t = io.open(fp, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in t else "\n"
    esc = nl + nl
    body, tail = t, ""
    if body.endswith(nl):
        tail = nl
        body = body[: -len(nl)]
    paras = body.split(esc)
    print("paras=", len(paras), "nl=", repr(nl))
    if not os.path.exists(bk):
        os.makedirs(os.path.dirname(bk), exist_ok=True)
        shutil.copyfile(fp, bk)
        print("backup created:", spec["backup"])
    else:
        print("backup reused")
    ok = True
    for e in spec["edits"]:
        i = e["i"]
        old = paras[i - 1]
        if e.get("prefix") and not old.startswith(e["prefix"]):
            print("!! PREFIX MISMATCH i=%d got=%r" % (i, old[:40]))
            ok = False
            continue
        if old == e["new"]:
            print("-- unchanged i=%d" % i)
            continue
        paras[i - 1] = e["new"]
        print("OK i=%d  %d -> %d chars" % (i, len(old), len(e["new"])))
    if not ok:
        print("ABORT: no write")
        return 1
    out = esc.join(paras) + tail
    io.open(fp, "w", encoding="utf-8", newline="").write(out)
    print("written", spec["file"], "chars", len(t), "->", len(out))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
