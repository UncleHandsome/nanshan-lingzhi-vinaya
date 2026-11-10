# -*- coding: utf-8 -*-
import io, json

path = "AI語譯/_work/review/fix_r8_g1.tsv"
raw = io.open(path, "rb").read()
assert b"\r" not in raw
lines = raw.decode("utf-8").split("\n")
assert lines[-1] == "", "must end with newline"
lines = lines[:-1]
print("lines:", len(lines))

segs = []
bad = []
for ln in lines:
    p = ln.split("\t")
    if len(p) != 4:
        bad.append(("cols", len(p), ln[:40]))
        continue
    b, c, s, t = p
    if b != "03_業疏":
        bad.append(("book", b))
    if not s.isdigit():
        bad.append(("seg", s))
    if "\n" in t or "\t" in t or t != t.strip():
        bad.append(("text", c, s))
    segs.append((c, s))
print("bad:", bad)
print("dup segs:", len(segs) - len(set(segs)))

# leftover target phrases that must be gone
leftovers = ["差派蓄徒眾", "原界若有惡比丘", "時間本就短促", "無德行", "反種苦業", "有作想而作法",
             "未來的諸比丘", "氣數", "被動承辦", "只觸碰了", "菩薩六度", "被治罰者", "外道凡夫",
             "癡狂", "縱容陳述", "開許五條戒", "過失性質是相同", "增加這三種說法", "護持自他之心",
             "抗議與與欲", "四人以上", "列報自他的兩種法名", "捨長衣等三人", "私己", "大綱的意思",
             "三種人界", "因順根機而設立教法", "出巡狩獵", "浮泛的議論", "明君正法治理", "界相不明顯",
             "構成別眾", "門扇", "問答和合同議", "行受戒、懺悔", "界外別眾僧", "送給別眾",
             "求受戒或懺罪", "正犯重戒", "隨順根機", "遍布在五道", "滿足法喜", "根本重過",
             "仍依原主命名", "在界內食用", "三世三乘", "未曾加法持咒", "自我約束檢點", "檢點約束自己",
             "（蟲傷）", "此五戒極為難得", "末世下劣", "真正的本體", "一切珍寶中皆能隨意自在",
             "在晝夜分別受戒", "若非依了義", "二有」互相抵消", "貪瞋癡", "不論早晚都予以節制",
             "求求解脫", "善來比丘身邊"]
found = []
for ln in lines:
    t = ln.split("\t")[3]
    for w in leftovers:
        if w in t:
            found.append((ln.split("\t")[2], w))
print("leftover hits:", found)

# new must differ from current for every row
rows = json.load(io.open("_r8_rows.json", encoding="utf-8"))
base = {}
for r in rows:
    base.setdefault((r["chunk"], r["seg"]), r["current"])
same = [k for k in segs if base[k] == [ln.split("\t")[3] for ln in lines if (ln.split("\t")[1], ln.split("\t")[2]) == k][0]]
print("unchanged rows:", same)
print("OK")
