# -*- coding: utf-8 -*-
"""7K 卷上之一（檔 9-37）套用工具。

用法（由 _7k01_run.py 呼叫）：
  apply(chunk, seg, [(old,new), ...], note)
- chunk: 01a_卷上之一 / 01b_卷上之一
- seg:  該 chunk 的非空行序（1 基）
只替換該行內出現恰一次的字串，其餘逐字保留；行尾依原檔。
每次寫檔前，首次改動會備份到 歸檔/7K卷修正前/01_行事鈔/<chunk>_v.txt。
"""
import os, sys, json, difflib

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(BASE, "AI語譯", "out", "01_行事鈔")
ARC = os.path.join(BASE, "歸檔", "7K卷修正前", "01_行事鈔")
LOG = os.path.join(os.path.dirname(__file__), "_7k01_edits.jsonl")


def _read(path):
    raw = open(path, "rb").read().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    parts = raw.split(nl + nl)
    return raw, nl, parts


def _nonempty_index(parts):
    return [i for i, p in enumerate(parts) if p.strip()]


def show(chunk, seg):
    raw, nl, parts = _read(os.path.join(OUT, chunk + ".txt"))
    idx = _nonempty_index(parts)
    part = parts[idx[seg - 1]]
    return part


def apply(chunk, seg, edits, note=""):
    path = os.path.join(OUT, chunk + ".txt")
    raw, nl, parts = _read(path)
    idx = _nonempty_index(parts)
    pi = idx[seg - 1]
    block = parts[pi]
    orig = block
    for old, new in edits:
        c = block.count(old)
        if c != 1:
            raise SystemExit("FAIL %s#%d count=%d: %r" % (chunk, seg, c, old[:40]))
        if new and new in block and new not in old:
            raise SystemExit("FAIL %s#%d new already present: %r" % (chunk, seg, new[:40]))
        block = block.replace(old, new)
    # 只在該行內變動；列出 diff 區塊供核對
    sm = difflib.SequenceMatcher(None, orig, block)
    ops = [(t, orig[i1:i2], block[j1:j2]) for t, i1, i2, j1, j2 in sm.get_opcodes() if t != "equal"]
    parts[pi] = block
    backup = os.path.join(ARC, chunk + "_v.txt")
    if not os.path.exists(backup):
        open(backup, "wb").write(raw.encode("utf-8"))
    open(path, "wb").write((nl + nl).join(parts).encode("utf-8"))
    rec = {"chunk": chunk, "seg": seg, "note": note,
           "edits": [{"old": o, "new": n} for o, n in edits],
           "diff": [{"op": t, "old": a, "new": b} for t, a, b in ops]}
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


if __name__ == "__main__":
    if sys.argv[1] == "show":
        print(show(sys.argv[2], int(sys.argv[3])))
