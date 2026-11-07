# -*- coding: utf-8 -*-
import csv, os, sys

base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯"
rev = os.path.join(base, "_work", "review")
out = os.path.join(base, "out")

def paras(book, chunk):
    with open(os.path.join(out, book, chunk + ".txt"), "r", encoding="utf-8-sig") as f:
        t = f.read().replace("\r\n", "\n")
    return [x for x in t.split("\n\n") if x.strip()]

def get(book, chunk, seg):
    return paras(book, chunk)[seg - 1]

def rep(book, chunk, seg, old, new):
    cur = get(book, chunk, seg)
    assert cur.count(old) == 1, (book, chunk, seg, "count", cur.count(old))
    return cur.replace(old, new)

rows = []

# 1. 04_比丘尼鈔 01b_卷上之上 85 -- 分項斷句：五生種非序數，第四併入三種例外，後續遞改
old = "第四、式叉摩那得為大尼授食，但除火淨五種生種及取金銀之外；第五、式叉摩那自從沙彌尼受食；第六、大比丘尼不得為式叉摩那宣說七聚罪名；第七、得語之云不淫、不殺、不妄語，如是等令其憶持；第八、式叉尼布薩日（隨僧說戒）；第九、至自恣日"
new = "第四、式叉摩那得為大尼授食，但經火作淨之五種生種、捉持金銀、以及自行從沙彌尼處受食這幾種情況除外；第五、大比丘尼不得為其宣說七聚罪名；第六、得告知「不淫、不殺、不妄語」等，令其憶持；第七、式叉尼布薩日（隨僧說戒）；第八、至自恣日"
rows.append(("04_比丘尼鈔", "01b_卷上之上", 85, rep("04_比丘尼鈔", "01b_卷上之上", 85, old, new)))

# 2. 04_比丘尼鈔 03b_卷中之上 3 -- 括注補明體例（十一項實列十門）
old = "（原文列數十一而名目舉十）"
new = "（原文標題作十一項，實列十項，疑為古抄脫漏或併項所致）"
rows.append(("04_比丘尼鈔", "03b_卷中之上", 3, rep("04_比丘尼鈔", "03b_卷中之上", 3, old, new)))

# 3. 03_業疏 04a_卷一之四 95 -- 清除英文提示詞殘留
rows.append(("03_業疏", "04a_卷一之四", 95,
             rep("03_業疏", "04a_卷一之四", 95, "There are sayings that: 縱使", "有人說：縱使")))

# 4. 02_戒疏 14a_卷三下之二 9 -- 同衣＝同類材質
rows.append(("02_戒疏", "14a_卷三下之二", 9,
             rep("02_戒疏", "14a_卷三下之二", 9, "收取「材質不同且不足製衣」的布料", "收取「同類材質但不足製衣」的布料")))

# 5. 02_戒疏 14b_卷三下之二 21 -- 補譯制意前半
cur = get("02_戒疏", "14b_卷三下之二", 21)
assert cur.startswith("因此託付給俗人掌管")
rows.append(("02_戒疏", "14b_卷三下之二", 21,
             "珍寶玉璧等貴重精華之物，是世俗人情所看重的，蓄存它們會滋長貪念、妨礙修道，引生過患極深，特別不是出世修道之人所適宜蓄存的。然而施主誠心布施，作為購買僧衣的價款，比丘唯恐犯下蓄寶之戒，不宜親自接受，" + cur))

# 6. 02_戒疏 14b_卷三下之二 79 -- 補譯《多論》句
cur = get("02_戒疏", "14b_卷三下之二", 79)
assert cur.startswith("外國用蠶綿製作衣服")
rows.append(("02_戒疏", "14b_卷三下之二", 79,
             "因此《薩婆多論》說：「所謂敷具，就是衣服的名稱。」" + cur))

# 7. 02_戒疏 14b_卷三下之二 87 -- 補譯不犯條
cur = get("02_戒疏", "14b_卷三下之二", 87)
assert cur.endswith("比丘尼違犯則結突吉羅罪。")
rows.append(("02_戒疏", "14b_卷三下之二", 87,
             cur + "不犯的情況：若是得到他人已做成的成品，應當用斧頭砍碎、和在泥中用來塗抹牆壁。"))

# 8. 02_戒疏 14b_卷三下之二 102 -- 補譯記文首句
cur = get("02_戒疏", "14b_卷三下之二", 102)
assert cur.startswith("自『而律文中』以下")
rows.append(("02_戒疏", "14b_卷三下之二", 102,
             "在第三點中，第一科。古人認為《四分律》注文列在不犯條款，所以說「與《十誦律》相同」。" + cur))

# 9. 02_戒疏 14b_卷三下之二 171 -- 補譯制意三句
cur = get("02_戒疏", "14b_卷三下之二", 171)
assert cur.startswith("世俗賢士尚且說過")
rows.append(("02_戒疏", "14b_卷三下之二", 171,
             "之所以制戒的原因：沙門脫離世俗修道，當以知足為首要。既然已經有了舊衣，就足以維持生命、長養道業。如今反而放縱情欲廣肆蓄存、大量積聚，滋長貪念敗壞道業，沒有比這更嚴重的了。" + cur))

# 10c_卷三上之一 76 已由 t2 批次於本回合修訂，不再重複處理。

# 驗證並輸出
lines = []
for book, chunk, seg, new in rows:
    assert "\n" not in new and "\r" not in new and "\t" not in new, (book, chunk, seg)
    assert new.strip() == new, (book, chunk, seg, "padding")
    old = get(book, chunk, seg)
    lines.append(f"{book}\t{chunk}\t{seg}\t{new}")
    print(f"{book} {chunk} {seg} old={len(old)} new={len(new)} changed={old != new}")

with open(os.path.join(rev, "fix_t1b.tsv"), "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines) + "\n")

print("ROWS", len(lines))
