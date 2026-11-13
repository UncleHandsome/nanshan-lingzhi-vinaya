# -*- coding: utf-8 -*-
"""7K 04_比丘尼鈔 卷中之上_b 第二輪潤飾（複讀後）。"""
import io, os, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT, "AI語譯", "out", "04_比丘尼鈔", "03b_卷中之上.txt")

EDITS = {
    53: [
        ("而盜賊從牆壁孔洞或屋內潛入竊取", "而盜賊從牆壁孔洞或屋內竊取"),
        ("這並非守護僧人的力量所能阻擋防範", "這並非守護者所能阻擋防範"),
        ("如今常有發好心替他人清洗整理缽器，因好心失手砸碎的",
         "如今常有人出於好心替他人清洗整理缽器，失手砸破的"),
        ("如果那人是指定布施給佛塔與僧團的", "如果是原本布施給佛塔與僧團的"),
    ],
    55: [
        ("《婆論》說：取非人物五錢已上，犯重偷蘭遮；四錢以下的，犯輕偷蘭遮。",
         "《婆論》說：盜取非人之物，值五錢以上的，犯重偷蘭遮；值四錢以下的，犯輕偷蘭遮。"),
    ],
    57: [
        ("一切鳥獸食殘，人去拿取的", "一切鳥獸吃剩的食物，人去拿取的"),
    ],
    59: [
        ("僧答說與盜者相同的，這些僧", "僧答說與盜者相同的話，這些僧"),
        ("哪怕只是移動界石標記一標", "哪怕只是移動一個界標"),
    ],
    61: [
        ("如果非敏感的輕處長了瘡癤癰疽", "如果是輕境處長了瘡癤癰疽"),
        ("若是敏感的重處生瘡", "若是重境處生瘡"),
        ("（鈔主）依義判云", "（鈔主）依義理判說"),
    ],
    63: [
        ("應當向其他人說出（發露）", "應當向其他人發露"),
        ("如果面對早就知情卻不肯發露的人，這兩個人都有過失",
         "如果向早就知情卻不肯發露的人發露，這兩個人都有過失"),
    ],
}


def main():
    with io.open(OUT, "r", encoding="utf-8", newline="") as f:
        raw = f.read()
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    n = 0
    for idx in sorted(EDITS):
        old = lines[idx - 1]
        cur = old
        for find, new in EDITS[idx]:
            c = cur.count(find)
            if c != 1:
                raise SystemExit("FIND 不唯一/不存在 line#%d count=%d %r" % (idx, c, find[:30]))
            cur = cur.replace(find, new)
        lines[idx - 1] = cur
        n += 1
        print("line#%d ok  %d ops" % (idx, len(EDITS[idx])))
    with io.open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write(eol.join(lines))
    print("二輪寫入 %d 段" % n)


if __name__ == "__main__":
    main()
