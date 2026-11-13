# -*- coding: utf-8 -*-
import os, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"

PATCHES = {
"05c_卷中之一": [
("因為這位有德的客僧能補足我處僧團法務教化的不足", "因為這樣的人能接替、代替我（佛）的位置（弘法領眾）"),
("僧人便拿劣質破爛器具盛裝食物給他", "僧人便拿粗劣的器皿盛裝食物給他"),
("這是針對那些泛泛無識、容易挑僧眾過失的一般俗人而言", "這是針對那些泛泛無識、會見僧眾過失（而生譏嫌）的一般俗人而言"),
("如同〈眾網〉法篇中所說", "如同〈僧網大綱篇〉中所說"),
("供應國王、大臣柴薪、火燭、燈油等", "供應國王、大臣柴薪、火炭、燈、燭等"),
("允許直接動用十九錢以內的資財", "允許直接動用十九錢的資財"),
("否則即是諂媚白衣（污家）", "給了就是污家（以僧物結好俗人、壞其正信）"),
("詳細情況如僧殘篇（二篇）末尾解說污家戒處所說", "詳細情況如僧殘篇（二篇）解說污家戒處所說"),
("依準世俗法律", "依準世俗僱傭的慣例"),
("其餘關於僧食通融與局限的詳細規定", "其餘關於僧食可通用與否的分際（通、局）的詳細規定"),
],
"05b_卷中之一": [
("聖教既然如此，就是極大的告誡。聖教已如此明誡而仍然違犯的，就是出於愚癡與憍慢。",
 "聖教既然如此，就是極大的告誡。因此在如此明誡之下仍然違犯的，就是出於愚癡與憍慢。"),
("若起上述四心之一，不名為得戒", "若起上述四心（善心、瞋恚、睡眠、狂亂）之一，不名為得戒"),
],
}

def main():
    for chunk, edits in PATCHES.items():
        path = os.path.join(ROOT, "AI語譯", "out", "01_行事鈔", chunk + ".txt")
        with open(path, "r", encoding="utf-8", newline="") as f:
            s = f.read()
        bad = []
        for old, new in edits:
            c = s.count(old)
            if c != 1:
                bad.append((c, old[:50]))
        if bad:
            for c, o in bad:
                print("COUNT", chunk, c, o)
            sys.exit(1)
        if "--apply" in sys.argv:
            for old, new in edits:
                s = s.replace(old, new)
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(s)
        print(chunk, "OK", len(edits))
    print("APPLIED" if "--apply" in sys.argv else "DRYRUN")

main()
