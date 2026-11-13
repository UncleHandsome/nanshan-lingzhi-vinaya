# -*- coding: utf-8 -*-
"""7K 校閱工具。
用法：
  python _7kq.py idx N              列出材料段（段號＋原文首句）
  python _7kq.py resp N             印出意見全文
  python _7kq.py seg N P1 P2 ...    印出指定段的原文與現譯全文
  python _7kq.py para N P           印出譯文段落全文
  python _7kq.py grep N 詞          在譯文/原文/記文中找含詞的段落
  python _7kq.py apply spec.json    套用編輯
"""
import os, re, io, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _7kq_lib import (ROOT, BOOK, rd, wr, load_material, load_paras, out_path,
                      src_path, resp)

def cmd_idx(n):
    segs = load_material(n)
    print(f"# 材料 {len(segs)} 段（檔 {n}）chunk={segs[0]['bookchunk'] if segs else '?'}")
    for s in segs:
        kind = s["orig"][:4]
        txt = s["orig"][4:] if kind.startswith("【") else s["orig"]
        print(f'{s["para"]:>3} {kind} {txt[:70]}')

def cmd_resp(n):
    t, src = resp(n)
    if t is None:
        print("意見檔不存在")
        return
    print(f"### resp_{n}（來源 {src}）")
    print(t)

def cmd_seg(n, plist):
    segs = load_material(n)
    d = {s["para"]: s for s in segs}
    bc = segs[0]["bookchunk"]
    paras = load_paras(bc)
    for p in plist:
        p = int(p)
        s = d.get(p)
        print(f"\n===== 段 {p} =====")
        if s:
            print("【原文】" + s["orig"])
        else:
            print("【原文】（材料未收）")
        print("【現譯】" + paras[p-1])

def cmd_para(n, plist):
    segs = load_material(n)
    bc = segs[0]["bookchunk"]
    paras = load_paras(bc)
    for p in plist:
        print(f"\n===== 段 {int(p)} =====\n{paras[int(p)-1]}")

def cmd_grep(n, kw):
    segs = load_material(n)
    bc = segs[0]["bookchunk"]
    paras = load_paras(bc)
    for i, t in enumerate(paras, 1):
        if kw in t:
            print(f"[譯文 {i}] {t[:160]}")
    for s in segs:
        if kw in s["orig"]:
            print(f"[原文 {s['para']}] {s['orig'][:160]}")

def cmd_apply(spec_path):
    spec = json.loads(rd(spec_path))
    by_chunk = {}
    for e in spec:
        by_chunk.setdefault(e["chunk"], []).append(e)
    total = 0
    for bc, edits in by_chunk.items():
        pf = out_path(bc)
        # 備份（已存在則沿用，不覆寫）
        arch = os.path.join(ROOT, "歸檔", "7K卷修正前", BOOK)
        os.makedirs(arch, exist_ok=True)
        bk = os.path.join(arch, bc + "_v.txt")
        if not os.path.exists(bk):
            wr(bk, rd(pf))
            print("備份", os.path.basename(bk))
        t = rd(pf)
        sep = "\r\n\r\n" if "\r\n" in t else "\n\n"
        parts = t.split(sep)
        for e in edits:
            p = e["para"]
            old = e["old"]; new = e["new"]
            cur = parts[p-1]
            cnt = cur.count(old)
            if cnt != 1:
                print(f"!! 段{p} old 出現 {cnt} 次：{old[:40]}")
                continue
            parts[p-1] = cur.replace(old, new, 1)
            total += 1
            print(f"OK 段{p} [{e.get('kind','')}] {old[:30]} → {new[:30]}")
        wr(pf, sep.join(parts))
        print("寫回", os.path.basename(pf))
    print("合計套用", total)

if __name__ == "__main__":
    a = sys.argv[1:]
    c = a[0]
    if c == "idx": cmd_idx(a[1])
    elif c == "resp": cmd_resp(a[1])
    elif c == "seg": cmd_seg(a[1], a[2:])
    elif c == "para": cmd_para(a[1], a[2:])
    elif c == "grep": cmd_grep(a[1], a[2])
    elif c == "apply": cmd_apply(a[1])
    else: print("unknown", c)
