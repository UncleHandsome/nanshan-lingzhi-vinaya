# -*- coding: utf-8 -*-
"""獨立驗證：備份 vs 現行，逐段比對（不依賴套用腳本的記憶體狀態）"""
import csv, hashlib, os, sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
os.chdir(ROOT)

with open(os.path.join("存疑材料", "待套用_re0.tsv"), encoding="utf-8", newline="") as f:
    recs = [r for r in csv.reader(f, delimiter="\t") if r and any(c.strip() for c in r)]
rows = recs[1:]
want = {}
for r in rows:
    want.setdefault(r[2], []).append((int(r[3]), r[4], r[0]))

ok_all = True
for chunk, items in want.items():
    name = [fn for fn in os.listdir(os.path.join("AI語譯", "out", "03_業疏"))
            if fn.endswith(".txt") and fn.startswith(chunk + "_")][0]
    base = os.path.splitext(name)[0]
    cur_p = os.path.join("AI語譯", "out", "03_業疏", name)
    bk_p = os.path.join("歸檔", "re0套用前", "03_業疏", base + "_r.txt")
    cur_b = open(cur_p, "rb").read()
    bk_b = open(bk_p, "rb").read()
    cur, bk = cur_b.decode("utf-8"), bk_b.decode("utf-8")
    cur_l, bk_l = cur.split("\n"), bk.split("\n")

    # 1. 行尾 / BOM
    crlf_ok = (cur.count("\r\n") == cur.count("\n")) and (bk.count("\r\n") == bk.count("\n"))
    bom_ok = not cur_b.startswith(b"\xef\xbb\xbf") and not bk_b.startswith(b"\xef\xbb\xbf")
    nl_ok = cur.count("\n") == bk.count("\n")

    # 2. 段落數
    pc = len([l for l in cur_l if l.rstrip("\r").strip()])
    pb = len([l for l in bk_l if l.rstrip("\r").strip()])

    # 3. 相異行 == 目標段
    diff = [i for i, (a, b) in enumerate(zip(bk_l, cur_l)) if a != b]
    tgt_idx = sorted(2 * (p - 1) for p, _, _ in items)
    diff_ok = diff == tgt_idx

    # 4. 目標段 == TSV 新段落；其餘逐字等於備份
    content_ok = True
    for p, newp, segid in items:
        i = 2 * (p - 1)
        if cur_l[i].rstrip("\r") != newp:
            content_ok = False
            print(f"  !! {chunk}#{p} 內容不符 TSV")
        if bk_l[i].rstrip("\r") == newp:
            print(f"  !! {chunk}#{p} 備份已等於新段落（原檔早就是新段落？）")
    other_ok = all(cur_l[i] == bk_l[i] for i in range(len(bk_l)) if i not in set(tgt_idx))

    ok = all([crlf_ok, bom_ok, nl_ok, pc == pb, diff_ok, content_ok, other_ok])
    ok_all &= ok
    print(f'{chunk} ({name}): 段數 {pb}->{pc} | 行數 {len(bk_l)}->{len(cur_l)} | 相異行 {len(diff)} '
          f'目標 {len(tgt_idx)} | CRLF only={crlf_ok} BOM-free={bom_ok} 換行數同={nl_ok} '
          f'僅目標段變={diff_ok} 其餘不動={other_ok} 內容正確={content_ok} => {"OK" if ok else "FAIL"}')
    print(f'   段序 {[p for p,_,_ in sorted(items)]}  sha256 cur={hashlib.sha256(cur_b).hexdigest()[:16]} '
          f'bk={hashlib.sha256(bk_b).hexdigest()[:16]}')

# 5. 備份內容 = 套用前原檔（可信度：備份 sha 應等於先前記錄的 before sha）
before = {"02a": "365452d7a3ad38e6", "02b": "e5a05ad81c61cfc3", "03a": "3351a1d30ac34f09"}
for chunk, h in before.items():
    name = [fn for fn in os.listdir(os.path.join("AI語譯", "out", "03_業疏"))
            if fn.endswith(".txt") and fn.startswith(chunk + "_")][0]
    base = os.path.splitext(name)[0]
    bh = hashlib.sha256(open(os.path.join("歸檔", "re0套用前", "03_業疏", base + "_r.txt"), "rb").read()).hexdigest()[:16]
    good = bh == h
    ok_all &= good
    print(f'備份 {base}_r.txt sha={bh} vs 套用前={h} => {"OK" if good else "FAIL"}')

print("\nRESULT:", "ALL OK" if ok_all else "FAIL")
sys.exit(0 if ok_all else 1)
