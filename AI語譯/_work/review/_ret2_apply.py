# -*- coding: utf-8 -*-
"""ret2 資持記：14 處譯文修正（dry 預設，--apply 才寫入）。"""
import sys, os, json, shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _ret2_lib as L

EDITS = [
    # (item, chunk, para_idx, old, new)
    ("1825-0005 第三句", "11d", 31,
     "徵意是推究第三（門）句數不定的緣由，不可與上文相混。",
     "徵意是推究第三句（即境想五句中的第三句，轉想與本迷結罪不定者）何以不定，不可與上文相混。"),

    ("1765-0002 初緣即文下眾", "10b", 54,
     "第一緣，即鈔文下所說的「眾」（大比丘）。",
     "第一緣，就是鈔文所指的「眾」（大比丘的衣鉢）。"),

    ("1918-0001 自觸具五", "14b", 12,
     "前半部分說明自己觸碰具備五種條件。",
     "前半部分說明自己觸碰具有五種情形（五類惡觸）。"),

    ("1918-0001 故食亦爾", "14b", 12,
     "第一句的註文說本來的食物也是如此",
     "第一句的註文說鉢中原本已受的剩餘食物（舊食）也是如此"),

    ("1919-0003 二互句", "14b", 20,
     "接著引用律文顯示「二互」的句子",
     "接著引用律文顯示「二互句」（即一有一無的兩種句子：手淨物不淨、物淨手不淨）"),

    ("1920-0001 七日自作", "14b", 23,
     "在沒有淨人的地方開許自己作淨，米放置滿七日後可以自己操作等。",
     "在沒有淨人的地方，先把米作淨之後，容許在七日之內自己煮食等。"),

    ("1924-0003 釋上不作二日", "14b", 45,
     "是解釋上面所說的「不能算作兩天」。",
     "是解釋上面所說的「不另作（剩餘的）兩天之法」（即不再只補足剩下的兩天期限）。"),

    ("1924-0001 雖具三義", "14b", 43,
     "雖然具備這三種義理",
     "手受的七日藥雖然也具備（體貴重、久延不變、氣味殊越）這三種義理"),

    ("1925-0003 同上防罪", "14b", 50,
     "所以與上面所防（所列）之罪相同",
     "所以與上面「防罪」（一科所論的罪相與名數）相同"),

    ("[補16] 孔雀咽", "14b", 58,
     "「孔雀咽」就是取孔雀頸部羽毛的青翠色",
     "「孔雀咽〔色〕」就是取孔雀頸部羽毛的青翠色"),

    ("1928-0002 通目三種", "14c", 2,
     "通指三種",
     "統稱（體、色、量）這三種條件"),

    ("1930-0006 明衣蓋", "14c", 17,
     "說明衣蓋",
     "說明護衣用的遮蓋物（防雨或保護衣物用的棚蓋之具）"),

    ("1643-0002 縱如來處", "07d", 40,
     "別人之物，即使（原）在如來之處；賊既自作主張（已成物主），不妨受用。",
     "別人的財物，縱使知道其來處（「如」疑為「知」字之形訛；亦可解作「縱使追溯其原本來處」）；賊既自為物主，不妨受用。"),
]


def main(apply=False):
    by_chunk = {}
    for it, ch, idx, old, new in EDITS:
        by_chunk.setdefault(ch, []).append((it, idx, old, new))

    ok = True
    report = []
    for ch, eds in by_chunk.items():
        p, t = L.load(ch)
        paras_before = len(L.paras(t))
        lines_before = t.count("\n")
        new_t = t
        for it, idx, old, new in eds:
            n = new_t.count(old)
            holder = None
            for i, pa in enumerate(L.paras(new_t), 1):
                if old in pa:
                    holder = i
            flag = "OK" if n == 1 else "!!"
            if n != 1:
                ok = False
            print("%s %-22s %s#%d  hits=%d  in_para=%s" % (flag, it, ch, idx, n, holder))
            if holder is not None and holder != idx:
                print("   !! 段落不符：預期 #%d，實得 #%d" % (idx, holder))
                ok = False
            if n == 1:
                new_t = new_t.replace(old, new)
        paras_after = len(L.paras(new_t))
        lines_after = new_t.count("\n")
        print("  %s: paras %d->%d  lines %d->%d  bytes %d->%d  CR=%d" %
              (ch, paras_before, paras_after, lines_before, lines_after,
               os.path.getsize(p), len(new_t.encode("utf-8")), new_t.count("\r")))
        if paras_before != paras_after or lines_before != lines_after or new_t.count("\r"):
            print("   !! 段數／行數／CR 檢查失敗")
            ok = False
        report.append((ch, p, t, new_t))

    print("\nALL OK" if ok else "\nHAS ERRORS")
    if apply and ok:
        for ch, p, t, new_t in report:
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write(new_t)
        print("written:", ", ".join(ch for ch, _, _, _ in report))


if __name__ == "__main__":
    main("--apply" in sys.argv)
