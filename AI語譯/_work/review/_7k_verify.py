# -*- coding: utf-8 -*-
"""套用後驗證：逐 chunk 與 _a 備份比對，只允許目標段相異；並檢查 06a 他手改動仍在。"""
import io, os, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT, "AI語譯", "out", "02_戒疏")
BAK = os.path.join(ROOT, "歸檔", "7K擋檔修正前", "02_戒疏")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _7k_spec import EDITS

def paras(path):
    t = io.open(path, encoding="utf-8", newline="").read()
    return [x for x in t.split("\n") if x.strip()], t

groups = {}
for chunk, seg, pairs in EDITS:
    groups.setdefault(chunk, []).append(seg)

print("=== 1) 與 _a 備份比對（相異段應等於目標段） ===")
allok = True
for chunk, segs in groups.items():
    cur, t = paras(os.path.join(OUT, chunk + ".txt"))
    old, t0 = paras(os.path.join(BAK, chunk + "_a.txt"))
    diff = [i + 1 for i, (a, b) in enumerate(zip(old, cur)) if a != b]
    ok = (diff == sorted(segs)) and len(cur) == len(old)
    allok &= ok
    print("%-14s paras %d->%d  crlf %d->%d  changed=%s  expect=%s  %s" % (
        chunk, len(old), len(cur), t0.count("\r\n"), t.count("\r\n"),
        diff, sorted(segs), "OK" if ok else "MISMATCH"))

print("\n=== 2) 06a：他手改動（96,97,101,104,105,130,133）是否保留 ===")
before, _ = paras(os.path.join(ROOT, "AI語譯", "_work", "review", "_7k_06a_before.txt"))
cur, _ = paras(os.path.join(OUT, "06a_卷二上之二.txt"))
q2, _ = paras(os.path.join(BAK, "06a_卷二上之二_q2.txt"))
d1 = [i + 1 for i, (a, b) in enumerate(zip(before, cur)) if a != b]
print("vs 套用前快照 相異段:", d1, "（應為我的目標段）")
their = [96, 97, 101, 104, 105, 130, 133]
kept = [s for s in their if cur[s - 1] == before[s - 1]]
print("他手改動保留:", kept, "共", len(kept), "/", len(their))
allok &= (kept == their)

print("\n=== 3) 目標段新文抽查 ===")
for chunk, seg, pairs in EDITS:
    cur, _ = paras(os.path.join(OUT, chunk + ".txt"))
    body = cur[seg - 1]
    miss = [old for old, new in pairs if old in body]
    print("%-14s #%-3d 舊文殘留=%s" % (chunk, seg, miss if miss else "無"))

print("\nALL OK" if allok else "\nFAIL")
