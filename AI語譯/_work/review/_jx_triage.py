# -*- coding: utf-8 -*-
"""從 resp 抽出四類（術語/主客/因果/範圍）候選條目，附該段是否已改。"""
import os, re, io, sys, json

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
RESP = os.path.join(ROOT, "batch_qwen", "r7k")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

KEY = [
    # 術語
    "術語", "名相", "專名", "讀反", "譯反", "反了", "相反", "顛倒", "詞義", "訓義",
    "名義", "定義", "義為", "此云", "三藏", "戒體", "作無作", "止作", "止犯", "作持",
    "通塞", "廣教", "略教", "羯磨", "波羅夷", "僧殘", "偷蘭", "突吉羅", "篇聚",
    "生造", "自造", "新造", "硬譯", "照搬",
    # 主客
    "主語", "主客", "能所", "能/所", "主動", "被動", "對象", "施受", "自他", "化他",
    "指代", "所指", "回指", "誰", "施者", "受者",
    # 因果
    "因果", "因位", "果位", "因中", "果頭", "倒果", "由因",
    # 範圍
    "範圍", "窄化", "過寬", "過窄", "限定", "全稱", "一概", "專指", "統攝", "含攝",
    "僅指", "只指", "兼", "局", "通局",
    # 經文/律文
    "經文", "律文", "戒本", "經處", "本經",
]


def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def main(nums):
    for n in nums:
        p = os.path.join(RESP, "resp_%s.txt" % n)
        if not os.path.exists(p):
            continue
        t = rd(p).replace("\r\n", "\n")
        print("\n===== resp_%s =====" % n)
        blocks = re.split(r"^###\s*【(\d{3,4}-\d{4})】(.*)$", t, flags=re.M)
        # blocks[0] = preamble; then triples
        if len(blocks) == 1:
            print("[無段標題]")
            print(t[:1500])
            continue
        pre = blocks[0].strip()
        if pre:
            print("[前言] " + re.sub(r"\n+", " / ", pre)[:400])
        for i in range(1, len(blocks), 3):
            no, title, body = blocks[i], blocks[i + 1], blocks[i + 2]
            items = re.findall(r"^\s*(?:\d+\.|[-*])\s*(.+)$", body, flags=re.M)
            hits = [it for it in items if any(k in it for k in KEY)]
            if not hits:
                continue
            print("\n--- %s %s" % (no, title.strip()[:60]))
            for h in hits:
                print("  * " + re.sub(r"\s*\n\s*", " ", h)[:500])


if __name__ == "__main__":
    main(sys.argv[1:])
