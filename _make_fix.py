# -*- coding: utf-8 -*-
import os, csv, sys

base = os.path.dirname(os.path.abspath(__file__))
REP = os.path.join(base, "AI語譯", "_work", "review", "report_t2.tsv")
OUTDIR = os.path.join(base, "AI語譯", "out")
DEST = os.path.join(base, "AI語譯", "_work", "review", "fix_p0_t2.tsv")


def load_paras(book, chunk):
    with open(os.path.join(OUTDIR, book, chunk + ".txt"), encoding="utf-8") as f:
        txt = f.read()
    paras = [x.strip() for x in txt.replace("\r\n", "\n").split("\n\n")]
    return [x for x in paras if x]


with open(REP, encoding="utf-8") as f:
    rows = list(csv.DictReader(f, delimiter="\t"))
p0 = [r for r in rows if r["level"] == "P0"]

# per-row plan: (base_source, [(old,new), ...]) or ("whole", text)
PLAN = {}

PLAN[0] = ("current", [(
    "被怨家強逼受辱而通體順從境況相合，則是「開」許不犯。若生受樂之心則結重罪，這是「遮」止。",
    "若被怨家強逼，即使二根相交（境合），只要不受樂便是「開」許不犯。若生受樂之心則結成重罪，這是「遮」止。",
)])

PLAN[1] = ("current", [(
    "正巧遇上國王出巡外出，便直接前往橫渡恆河。國王發覺後趕忙追趕，直到河中央才追上。",
    "正巧遇上國王正在睡覺，便直接前往橫渡恆河。國王醒來後急忙追趕，追到河中央才追上。",
)])

PLAN[2] = ("current", [(
    "例如邊遠地區受五戒者允許頻繁洗澡",
    "例如邊遠地區開許五人僧受具足戒，且允許頻繁洗澡",
)])

PLAN[3] = ("current", [(
    "犯波逸提罪（單墮）受報三億六萬歲",
    "犯提舍尼罪受報三億六萬歲",
)])

_sapu = (
    "能徹底破斥外道，宣說一切種類的有情眾生全都可以納受戒體，",
    "能徹底破斥外道『主張一切有情皆可受戒』之說，",
)
PLAN[4] = ("current", [_sapu])
PLAN[5] = ("current", [_sapu])

PLAN[6] = ("out", [(
    "克服魔障不免破戒",
    "為魔所降（被欲魔降伏）而不免將要破戒",
)])

PLAN[7] = ("out", [(
    "把人與物品合併起念取奪的情況而說",
    "對一切人類的財物通同起心盜取的情況而說",
)])

PLAN[8] = ("current", [(
    "如果奴婢隨其言語逃跑，比丘犯吉羅罪",
    "話剛一說出口比丘即犯吉羅罪",
)])

PLAN[9] = ("out", [(
    "若是外寺僧人自家帶來的奴僕牲畜食用",
    "若是該寺僧團常住所有的奴僕牲畜食用",
)])

PLAN[10] = ("whole", "【記文】回答：「戒律所禁制的對象是未受具足戒者，並不禁止向同受具戒、同心同見的道友宣說。」")

PLAN[11] = ("out", [(
    "且引發的情感苦惱極其盈滿奔流，所以判輕",
    "備歷艱辛費力才得以分泌流溢，所以判輕",
)])

PLAN[12] = ("whole", "【疏文】在制戒因緣中，俗家女人的譏笑有兩種面向，如同《薩婆多論》所說：「這些婦女為何前來呢？第一、因為世俗事務繁忙勞碌，見出家人住處寂靜安樂的緣故；第二、因為跟隨善友知識前來聽聞佛法的緣故；第三、因為僧房莊嚴修整值得觀賞的緣故。她們為何進入僧房呢？因為認為出家人已斷除貪欲身心清淨，深信無疑的緣故。她們為何有的笑、有的罵呢？第一、因為各人心中欲念多寡不同的緣故；第二、因為與僧人熟識或不熟識的緣故；第三、因為有的喜歡隱蔽、有的喜歡公開的緣故；第四、有親屬在場便畏懼指責而斥罵，無親屬在場則無所顧忌而歡笑的緣故。」這些情況應當明瞭。")

PLAN[13] = ("current", [(
    "縱然真的迷惘無知，也不是藉口不學就能推託免罪的，依法仍要結罪。正因為房舍造作事關重大，極容易產生嚴重的根本毀犯，所以才特別將這第三句完整列出。」",
    "縱然依常例而言，非因不學而生之迷忘本來不結罪；但因造房事關重大，唯恐有人藉口迷忘而犯根本大罪，所以才特別列出第三句。」",
)])

PLAN[14] = ("out", [(
    "這三個階次之所確立，所言皆無非關聖法的世俗之事。",
    "這三個階次之所確立，所涉及的無非都是世間俗事。",
)])

PLAN[15] = ("whole", "【疏文】《十誦律》說：「如果有人寫信自稱證得初果，並將信件展示給他人看；信中雖聲稱證果，而自身實際上並未證得，這犯偷蘭遮罪。」")

assert len(p0) == 16, len(p0)
assert set(PLAN) == set(range(16))

lines = []
log = []
fails = 0
for i, r in enumerate(p0):
    book, chunk, seg = r["book"], r["chunk"], str(r["seg"])
    mode = PLAN[i]
    cur_rep = (r.get("current") or "").strip()
    paras = load_paras(book, chunk)
    cur_out = paras[int(seg) - 1]

    if mode[0] == "whole":
        new = mode[1]
        base_txt = cur_rep if cur_rep else cur_out
        log.append("[%d] %s %s %s WHOLE (base=%s len %d -> %d)" % (
            i, book, chunk, seg, "current" if cur_rep else "out", len(base_txt), len(new)))
    else:
        src, ops = mode
        base_txt = cur_rep if src == "current" else cur_out
        if src == "current" and not cur_rep:
            log.append("[%d] !! current empty but plan wanted current" % i)
            fails += 1
            lines.append("%s\t%s\t%s\tSKIP:current 為空" % (book, chunk, seg))
            continue
        new = base_txt
        for old, rep in ops:
            c = new.count(old)
            if c != 1:
                log.append("[%d] !! MATCH COUNT %d for %r" % (i, c, old[:40]))
                fails += 1
                break
            new = new.replace(old, rep)
        else:
            log.append("[%d] %s %s %s base=%s len %d -> %d  OK" % (
                i, book, chunk, seg, src, len(base_txt), len(new)))
            if new == base_txt:
                log.append("[%d] !! no change" % i)
                fails += 1
                continue
        log.append("")

    if any(ch in new for ch in "\t\r\n"):
        log.append("[%d] !! TAB/NL in new" % i)
        fails += 1
        continue
    if not new.strip():
        log.append("[%d] !! empty new" % i)
        fails += 1
        continue
    lines.append("%s\t%s\t%s\t%s" % (book, chunk, seg, new))

log.insert(0, "P0 rows=%d  emitted=%d  fails=%d" % (len(p0), len(lines), fails))
with open(os.path.join(base, "_fixlog.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(log))

print("\n".join(log))
print("LINES:", len(lines), "FAILS:", fails)

if fails == 0 and len(lines) == len(p0):
    with open(DEST, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("WROTE", DEST)
else:
    print("NOT WRITTEN")
