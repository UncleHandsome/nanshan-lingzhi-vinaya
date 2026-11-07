# -*- coding: utf-8 -*-
import csv, io, os, difflib
raw = open(r"AI語譯/_work/review/report_t1pack.tsv", encoding="utf-8-sig").read()
R = list(csv.reader(io.StringIO(raw), delimiter="\t"))[1:]
assert len(R) == 69, len(R)
cur = [r[9] for r in R]
new = [c.replace("\r\n","\n").replace("\n","") for c in cur]

def rep(i, old, s):
    assert new[i].count(old) == 1, (i+1, "count", new[i].count(old), old[:30])
    new[i] = new[i].replace(old, s)

# row 1  (資持記 01c 18) 三種羯磨番次增減
rep(0, "三種羯磨作法，人數增加則愈善，人數減少則不能成就，這就叫做「法無準則」。",
       "對於單白、白二、白四這三種羯磨作法，多加宣告番次則認為更善，減少番次則不能成就，這就叫做「法無準則」。")

# row 2  (01d 16) 刪除跨段溢譯末句
rep(1, "；又如《僧祇律》仍採用了已被廢除之教（牒事說欲），《四分律》則採用了後興之正制（不牒事）之類。",
       "。")

# row 3  (01d 27) 有不足之義 = 不足數
rep(2, "這在義理上顯然有所不足，",
       "本宗雖無明文，但具有此人不具備受捨資格（不足數）的義理，")

# row 4  (01d 61) 三小界
rep(3, "例如三個小自然界不需要另外樹立界相標記，直接依據三個小自然界的羯磨文來予以通決；",
       "例如三種小界不需要另外樹立標相，直接依據三小界的羯磨文來予以通決；")

# row 5  (01e 40) 補回漏譯前半
rep(4, "第二單提中比丘尼缺少三條戒（",
       "在戒條有無互缺之中有兩種：第一是三十捨墮中比丘尼缺少二條戒（一是雨季前提早索求雨衣，二是住阿蘭若處離衣宿）；第二是九十單提中比丘尼缺少三條戒（")

# row 7  (02c 47) 四羯磨人 = 受治罰者
rep(6, "〔指四種能作羯磨的人，見第四條例。〕",
       "〔指受四種治罰羯磨處分的人，見第四條例。〕")

# row 8  (02c 60) 白二遙加 / 解方入數
rep(7, "以白二羯磨遙相加持，能理解之時方得計入僧數，",
       "以白二羯磨施加與癡狂羯磨處置，必須待僧團行羯磨解除處分後方得計入僧數，")

# row 9  (02d 4) 二師所為並不須
rep(8, "唯恐有人以為其餘的人也必須如此，其實兩位戒師所作的事本來都不需要這樣。",
       "這是唯恐有人以為只有其餘僧眾才須如此，而誤認二師與所為之人並不需要，所以鈔文特予指明。")

# row 10 (02d 8) 五十祇中
rep(9, "在《僧祇律》的五人僧與十人僧受戒中，和尚都是算在法定人數之外；《四分律》則限定在中國（中印度）必須十人。",
       "在《五分律》、《十誦律》、《僧祇律》中，和尚都是算在法定十人之外；《四分律》則限定中國受戒十人僧（已含和尚）。")

# row 11 (行事鈔 01b 22) 說不稱欲
rep(10, "問：向僧中宣說代受之欲時，若未稱說與欲人的姓名，法事算成就嗎？",
        "問：向僧中宣說欲法時，若文辭與受託之欲不相稱符，法事算成就嗎？")

# row 12 (行事鈔 01b 61) 四人對首自恣
rep(11, "四人面對面的心念自恣", "四人對首自恣")

# row 13 (01a 26) 段首孤立右括號
assert new[12].startswith("）")
new[12] = new[12][1:]

# row 14 (01b 15) 臆下三句 / 衣藥
rep(13, "「臆」字以下的兩句", "「臆」字以下的三句")
rep(13, "〔例如手持衣物陳棄藥、執持臥具當作多餘被褥之類。〕",
        "〔例如守持衣物與藥物、執持臥具當作多餘被褥之類。〕")

# row 17 (行事鈔 01a 41) 僧坊院相同村界
rep(16, "如今僧坊周圍的院牆界標，如果與聚落的界標無法分開，就不需要到方圓五里之內去召集所有僧人。",
        "如今僧坊四周的圍院相狀，與律中聚落的四種界相並無分別（皆有牆垣圍繞），因此便同於村界，不需要到蘭若方圓五里之內去召集僧人。")

# row 18 (02c 38) 三種單白 / 五人僧
rep(17, "邊地受戒的兩種法事、教授師單白召請、戒師當面審問、自恣時單白和僧，只有這三種單白羯磨，是由五人來使用。",
        "邊地受戒的兩種法事（即教授師單白召請、戒師當面審問），加上自恣時單白和僧，只有這三種單白羯磨，是由五人僧來執行。")

# row 20 (行事鈔 01b 67) 人非：五人秉四人对首
rep(19, "第一是「人非」，四個人便可主持眾僧法，卻由五個人中一人受欲而作對首，或者參與者並非戒律清淨，明知其破戒卻仍與他共同作法。",
        "第一是「人非」，界內明明已有五人，卻由四人秉法、第五人給受欲意來作對首自恣（界滿五人應作眾法，且對首法不開受欲）；或者參與者戒行不淨，明知其破戒仍與他共同作法。")

changed = [i for i in range(69) if new[i] != cur[i].replace("\n","")]
print("changed", len(changed), [i+1 for i in changed])
for i in range(69):
    assert "\n" not in new[i] and "\t" not in new[i] and new[i].strip() == new[i] and new[i]
    assert 100 < len(new[i]) < 700, (i+1, len(new[i]))
out = os.path.join("AI語譯/_work/review", "fix_t1pack.tsv")
with open(out, "w", encoding="utf-8", newline="\n") as f:
    for i, r in enumerate(R):
        f.write("%s\t%s\t%s\t%s\n" % (r[0], r[1], r[2], new[i]))
print("wrote", out)

# verify dump
buf=[]
for i,r in enumerate(R):
    buf.append("=== %d | %s | %s | %s | %s ===" % (i+1, r[0], r[1], r[2], "CHANGED" if i in changed else "same"))
    if i in changed:
        sm=difflib.SequenceMatcher(None, cur[i].replace("\n",""), new[i])
        for tag,i1,i2,j1,j2 in sm.get_opcodes():
            if tag!="equal":
                buf.append("%s: OLD[%s] NEW[%s]" % (tag, cur[i].replace("\n","")[i1:i2], new[i][j1:j2]))
open("AI語譯/_work/review/_t1pack_verify.txt","w",encoding="utf-8").write("\n".join(buf)+"\n")
print("verify dumped")
