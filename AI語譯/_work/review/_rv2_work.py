# -*- coding: utf-8 -*-
"""resp 條目標題清單（每行一條）+ 可依段號取詳細。
用法: python _rv2_work.py heads 844 845     -> _rv2/h_NNN.txt / 印出
      python _rv2_work.py item 844 0003 0010
"""
import os, sys, re, io

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
sys.path.insert(0, os.path.join(ROOT, "AI語譯", "_work", "review"))
from _rv_kit import parse_x7, cur_of  # noqa
from _rv2_dig import split_items, SEGNO  # noqa

RESP = os.path.join(ROOT, "batch_qwen", "r7k")
VIEW = os.path.join(ROOT, "AI語譯", "_work", "review", "_rv2")


def load(nnn):
    text = io.open(os.path.join(RESP, "resp_%s.txt" % nnn), encoding="utf-8").read()
    text = re.sub(r"(?m)^([\s#*\-•·]*)(【)(\d{4})(】)",
                  lambda m: m.group(1) + "【" + nnn + "-" + m.group(3) + "】", text)
    return text, split_items(text), {s["no"]: s for s in parse_x7(nnn)}


def heads(nnn):
    text, items, d = load(nnn)
    out = []
    for i, (nos, body) in enumerate(items, 1):
        first = body.split("\n")[0].strip()
        first = re.sub(r"^[#*\-\s]+", "", first)
        st = ""
        for no in nos:
            s = d.get(no)
            if not s:
                continue
            st += ("改" if cur_of(s) != s["tr"] else "拒")
        out.append("%s|%s|%s" % (st, nos[0], first[:78]))
    return out


def item(nnn, want):
    text, items, d = load(nnn)
    for nos, body in items:
        if not any(n.split("-")[1] == w.zfill(4) for n in nos for w in [want]):
            continue
        for no in nos:
            s = d.get(no)
            if not s:
                continue
            print("\n=== %s [%s]" % (no, "改" if cur_of(s) != s["tr"] else "拒"))
            print("[原文] " + s["src"])
            print("[材料] " + s["tr"])
            print("[現行] " + cur_of(s))
            break
        print("[意見] " + body)
        return
    print("(無此段)")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "heads":
        for n in sys.argv[2:]:
            for ln in heads(n):
                print("%s\t%s" % (n, ln))
    elif cmd == "item":
        item(sys.argv[2], sys.argv[3])
