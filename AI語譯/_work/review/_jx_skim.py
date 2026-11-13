# -*- coding: utf-8 -*-
"""resp 精簡瀏覽（容忍多種標題格式）：每段輸出壓縮後全文（可截斷）。"""
import os, re, io, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
RESP = os.path.join(ROOT, "batch_qwen", "r7k")


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def clean(s):
    s = re.sub(r"\*\*|__|`|^#+\s*", "", s, flags=re.M)
    s = re.sub(r"^\s*[-*]{3,}\s*$", "", s, flags=re.M)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n+", " ¶ ", s)
    s = re.sub(r"\n", " ", s)
    return s.strip()


def dedup(t):
    # 去掉明顯重複貼上的後半段
    n = len(t)
    if n > 2000 and t[n // 2:] and t[:n // 2].find(t[n // 2:n // 2 + 60]) >= 0:
        return t[:n // 2]
    return t


def main(maxchars, nums):
    mc = int(maxchars)
    for n in nums:
        p = os.path.join(RESP, "resp_%s.txt" % n)
        if not os.path.exists(p):
            print("\n===== resp_%s MISSING =====" % n)
            continue
        t = dedup(rd(p).replace("\r\n", "\n"))
        print("\n===== resp_%s =====" % n)
        parts = re.split(r"【(\d{3,4}-\d{4})】", t)
        pre = clean(parts[0])
        if pre:
            print("[前言] " + pre[:400])
        if len(parts) == 1:
            print(clean(t)[:mc])
            continue
        for i in range(1, len(parts), 2):
            no, body = parts[i], clean(parts[i + 1])
            if not body:
                continue
            print("\n-- " + no + "：" + (body[:mc] + ("…" if len(body) > mc else "")))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
