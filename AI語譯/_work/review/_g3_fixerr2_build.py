# -*- coding: utf-8 -*-
"""Build fix_err2_g3.tsv for book 02_戒疏 from report_err2.tsv.

Each output paragraph = report `current` verbatim, with only the pointed
problem spans replaced by the report's `suggestion` wording.
Rows whose problem sentence cannot be found in `current` are skipped.
"""
import io, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(BASE, "report_err2.tsv")
OUT = os.path.join(BASE, "fix_err2_g3.tsv")
BOOK = "02_戒疏"

# row number (1-based among 02_戒疏 rows, in report order) -> [(old, new), ...]
EDITS = {
    1: [("身為佛陀四依弟子的大使，可謂獨力支撐維繫正法之人",
         "身為四依大士，使得維繫正法的重任全繫於他一人而已")],
    2: [("唯一讓人遺憾的是，《戒本疏》、《行宗記》以及科文，這四種版本各自單獨流行",
         "唯一讓人遺憾的是，《戒本》、《戒本疏》、《行宗記》以及科文，這四種書本各自單獨流行")],
    3: [("鋪陳演繹義理門類，豈敢在現今學人面前度量呈顯自己的淺薄器識",
         "鋪陳演繹義理門類，則冒昧將自己的才識呈示於當今與後世學人")],
    4: [("就好比遇到疾病因緣，病情嚴重的要用擔架抬來會場，病情較輕的則由僧眾親自前往探視作法，這點大家應當明了",
         "況且如疾病因緣，病重能移者用擔架抬來僧中，不能移動且人數少者則由僧眾親往其處作法，依此即可明白")],
    6: [("卷十四：月望布薩戒以下",
         "卷十四：月望衣戒（月望戒）以下")],
    7: [("這乃是戒、定、慧三學之修持的宏大綱領",
         "這乃是南山律三行（眾行、自行、共行）的宏大綱領")],
    10: [("「對於有罪過的事，修行者應受制止約束；對於無罪過的事，修行者則聽許開行。」",
          "「若是有罪過的行為，佛法便予以禁制；若是無罪過的行為，佛法便予以聽許開行。」")],
    11: [("前三心雖然本身不是善惡記性，但當初所受的戒體卻是善性的記號",
          "前三心雖然本身不是善惡記性（屬無記），但當初所受的戒體卻是有記之善性")],
    12: [("「罪相」是指波羅夷、僧殘、波逸提、突吉羅等各級戒罪",
          "「罪相」是指波羅夷、偷蘭遮、波逸提、突吉羅等各級戒罪")],
    13: [("依循這項原則修行，就不會執著於功利",
          "若僅依此世樂而修行，就不能稱為利根（不名為利）")],
    14: [("「八戒期心，盡夜分終，故捨。」",
          "「八關齋戒的誓願是以夜晚結束（至次日天明）為期，所以期限一到便自然捨戒。」")],
    15: [("例如誤以為自己擁有處分權、誤以為是無主物等情況",
          "例如誤以為是經僧團指授處分之地、誤以為是無主物等情況")],
    16: [("只要財物價值達到半錢至滿五錢的標準，就結犯根本重罪",
          "只要分得的半件衣服價值達到滿五錢的標準（半衣邊滿），就結犯根本重罪")],
    17: [("藥有兩種，毒殺惡物的藥與救活生命的藥，同樣都冠以藥的美名。例如第一篇予以徹底斷滅棄絕，就如同用來殺死惡疾的猛藥一樣",
          "藥有兩種，殺人之藥（毒藥）與救活人之藥，同樣都冠以藥的名稱。例如第一篇予以徹底滅擯棄絕，就如同能致人於死的毒藥一樣")],
    18: [("無非都不出對單人懺悔的範疇",
          "並非沒有對首懺悔的法門")],
    19: [("波逸提在懺悔時，三種說詞並無二致",
          "波逸提在懺悔時，同屬宣告三遍之悔法（三悔）而無差別")],
    20: [("那麼與天女行淫", "那麼與天人行淫")],
    21: [("所以智光律師說", "所以慧光律師說")],
    22: [("即使不隱覆罪過而獲准懺悔，以及犯戒受戒戒品不足數者",
          "即使因不隱覆罪過而獲准懺悔（作學悔），以及在僧團法事中不得算入法定僧數（及不足數）")],
    23: [("如果根據罪相純一或混雜來劃分，前四篇屬於純一究竟罪，後三篇則屬於混雜罪",
          "如果根據罪相純一或混雜來劃分七聚，前四聚屬於純一究竟罪（均），後三聚則屬於兼攝因罪的混雜罪（雜）")],
    24: [("此生報應的時間極其短暫，死後受報就在眼前",
          "來生受報（生報）之期為時不久")],
}
# rows whose pointed sentence is absent from `current` (labels point elsewhere)
SKIP = {
    5: "current 為科判標題，problem 所指「犯下諸罪應聞上篇」在 current 中找不到",
    8: "current 為 03c 記文，problem 所指「三種請懺法／發露言詞」不在其中",
    9: "current 為 04b 下一段記文，problem 所指「原先是偷蘭遮」不在其中",
}


def read_rows(path):
    with io.open(path, encoding="utf-8-sig") as f:
        lines = f.read().split("\n")
    hdr = lines[0].rstrip("\r").split("\t")
    rows = []
    for ln in lines[1:]:
        ln = ln.rstrip("\r")
        if not ln.strip():
            continue
        f = ln.split("\t")
        if len(f) != len(hdr):
            continue
        rows.append(dict(zip(hdr, f)))
    return [r for r in rows if r["book"] == BOOK]


def main():
    rows = read_rows(REPORT)
    print("02_戒疏 rows:", len(rows))
    assert len(rows) == 24, len(rows)
    for n, r in enumerate(rows, 1):
        print(f"{n:2d} {r['gid']:8s} {r['chunk']:16s} seg={r['seg']:>3s}")

    out_lines = []
    done = 0
    for n, r in enumerate(rows, 1):
        cur = r["current"]
        if n in SKIP:
            print(f"SKIP {n}: {SKIP[n]}")
            continue
        edits = list(EDITS[n])
        # rows 1,2 share the same paragraph: apply both fixes to both outputs
        if n == 1:
            edits += EDITS[2]
        if n == 2:
            edits = list(EDITS[1]) + list(EDITS[2])
        t = cur
        for old, new in edits:
            c = t.count(old)
            if c != 1:
                raise SystemExit(f"row {n}: expected 1 occurrence, found {c}: {old[:50]}")
            t = t.replace(old, new)
        if t == cur:
            raise SystemExit(f"row {n}: unchanged")
        for bad in ("\t", "\n", "\r"):
            if bad in t:
                raise SystemExit(f"row {n}: bad char {bad!r}")
        assert "\t" not in r["book"] and "\t" not in r["chunk"] and "\t" not in r["seg"]
        out_lines.append(f"{r['book']}\t{r['chunk']}\t{r['seg']}\t{t}")
        done += 1
        delta = len(t) - len(cur)
        print(f"OK {n:2d} len {len(cur)} -> {len(t)} ({delta:+d})")

    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        for ln in out_lines:
            f.write(ln + "\n")
    print("wrote", OUT, "lines:", len(out_lines), "done:", done, "skipped:", len(SKIP))


if __name__ == "__main__":
    main()
