# -*- coding: utf-8 -*-
"""複審套用：10c／10d 經文→戒文、因位果位→因罪果罪。
每個 find 必須在該檔唯一（mode=one）或全域（mode=all，印次數）。
"""
import io, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = ROOT + r"\AI語譯\out\02_戒疏"

OPS = {
 "10c_卷三上之一.txt": [
   ("one", "經文末尾結成僧殘罪", "戒文末尾結成僧殘罪"),
   ("one", "接下來解釋戒本經文，在總體劃分之中", "接下來解釋戒本，在總體劃分之中"),
   ("one", "解釋第一雙之中的經文。", "解釋第一雙之中的戒文。"),
 ],
 "10d_卷三上之一.txt": [
   ("one", "依照此處私下勸誡的經文", "依照此處私下勸誡的文句"),
   ("one", "在戒本經文當中，章法結構", "在戒本當中，章法結構"),
   ("one", "解釋經文當中。首先總體提示", "解釋文句當中。首先總體提示"),
   ("one", "戒本經文中雖然沒有「順從」", "戒本中雖然沒有「順從」"),
   ("one", "解釋經文，容易明白", "解釋戒文，容易明白"),
   # 因果術語
   ("all", "因位罪業", "因罪業"),
   ("all", "因位小罪", "因罪"),
   ("all", "因位與果位", "因與果"),
   ("all", "因位的突吉羅", "因罪突吉羅"),
   ("all", "果位的突吉羅", "果罪突吉羅"),
   ("all", "因位突吉羅", "因罪突吉羅"),
   ("all", "果位突吉羅", "果罪突吉羅"),
   ("all", "因位罪", "因罪"),
   ("all", "果位罪", "果罪"),
   ("one", "以未念完為因位，以念完為果位", "以未念完為因罪，以念完為果罪"),
   ("one", "果位既然是偷蘭遮，因位因此便犯突吉羅", "果罪既然是偷蘭遮，因罪因此便犯突吉羅"),
   ("one", "一旦全體完成就是果位的僧殘罪", "一旦全體完成就是果罪的僧殘罪"),
   ("one", "才達到最終的果位僧殘罪", "才達到最終的僧殘果罪"),
   ("one", "因位是偷蘭遮罪", "因罪是偷蘭遮罪"),
   ("one", "果位只結突吉羅罪", "果罪只結突吉羅罪"),
 ],
}

if __name__ == "__main__":
    dry = "--apply" not in sys.argv
    for fn, ops in OPS.items():
        p = OUT + "\\" + fn
        t = io.open(p, encoding="utf-8", newline="").read()
        orig = t
        for mode, find, new in ops:
            c = t.count(find)
            if mode == "one" and c != 1:
                raise SystemExit("FAIL %s [%s] count=%d" % (fn, find, c))
            t = t.replace(find, new)
            print("%-22s %-3s %-28s -> %-28s cnt=%d" % (fn, mode, find, new, c))
        if dry:
            print("[dry] %s 變更字元 %d" % (fn, len(t) - len(orig)))
        else:
            io.open(p, "w", encoding="utf-8", newline="").write(t)
            print("[write] " + fn)
