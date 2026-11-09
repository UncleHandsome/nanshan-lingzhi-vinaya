# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review\_te1")
from segdump_lib import load

OUTTSV = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review\fix_te1.tsv"

# (book, chunk, seg) in user's list order (07b#31 listed twice, one row only)
KEYS = [
    ("01_行事鈔", "06c_卷中之二", 6),
    ("資持記", "08d_中二", 32),
    ("資持記", "08d_中二", 45),
    ("01_行事鈔", "07b_卷中之三", 30),
    ("01_行事鈔", "07b_卷中之三", 31),
    ("資持記", "10a_中三下", 7),
    ("資持記", "10a_中三下", 11),
    ("資持記", "10a_中三下", 12),
    ("資持記", "10a_中三下", 13),
    ("資持記", "15d_下三", 5),
    ("資持記", "09a_中三上", 21),
    ("01_行事鈔", "07a_卷中之三", 3),
    ("資持記", "10a_中三下", 16),
    ("資持記", "10a_中三下", 5),
]

# targeted replacements: key -> [(old, new), ...]
REPL = {
    ("01_行事鈔", "06c_卷中之二", 6): [
        ("對施主說：「放在這裡面，我知道了。」",
         "對施主說：「你放在這裡（是中知）。」"),
    ],
    ("資持記", "08d_中二", 32): [],
    ("資持記", "08d_中二", 45): [
        ("所以特別指出遮戒是透過白四羯磨才得戒。從「諸」字以下",
         "所以特別指出遮戒是透過白四羯磨才得戒】。從「諸」字以下"),
    ],
    ("01_行事鈔", "07b_卷中之三", 30): [
        ("《僧祇律》所定的五種正食也是與此相同。",
         "《僧祇律》所定的五種正食也是與此（前面《十誦律》之五正食）相同。"),
    ],
    ("01_行事鈔", "07b_卷中之三", 31): [],
    ("資持記", "10a_中三下", 11): [
        ("不作殘食法便犯提舍尼罪",
         "不作殘食法便犯波逸提罪（單提）"),
        ("來裝乾飯",
         "來裝麨（炒麥粉）"),
    ],
    ("資持記", "10a_中三下", 12): [
        ("淨人分發乾飯",
         "淨人分發麨"),
        ("自己帶有乾飯袋",
         "自己帶有麨袋（炒糧袋）"),
        ("施主以為比丘需要乾飯",
         "施主以為比丘需要麨"),
    ],
    ("資持記", "10a_中三下", 13): [
        ("施主拿著比丘的乾飯袋遞給他",
         "施主拿著比丘的麨袋遞給他"),
    ],
    ("資持記", "15d_下三", 5): [],
    ("資持記", "09a_中三上", 21): [
        ("讓對方去看而見不到獵物，所以注釋說方便等。",
         "讓獵人去看而見不到野獸，所以注釋才說是方便引接之法等。"),
    ],
    ("01_行事鈔", "07a_卷中之三", 3): [],
    ("資持記", "10a_中三下", 16): [
        ("又在身綺互戒中，比丘尼接受了不作餘食法的食物，由此證明僧尼兩眾同樣具有此法，這是顯而易見的。",
         "又在身口綺戒的身綺（觸惱戒）開緣中，比丘尼亦有受持『不作餘食法』頭陀行之開許，由此證明僧尼兩眾同樣具有此法，這是顯而易見的。"),
    ],
    ("資持記", "10a_中三下", 5): [
        ("因為餅屬於正食",
         "因為麨（炒米麥粉）屬於正食"),
        ("解釋最初的因緣，在食物的種類中，《十誦律》分為三類",
         "在解釋第一條犯緣（食物本體）中，《十誦律》分為三類"),
    ],
}

# 10a#7: full reconstruction (previous wholesale replacement had dropped the
# 四中 / 五雜正 / 佉闍尼 sentences; all three review items for this seg need them)
SEG7 = (
    "在第四項「磨食」中，稻穀原本屬於正食，麥屬於似正食；但因為研磨得十分細碎，"
    "所以歸入不正食中收錄。〔以上《十誦律》總共列出十五種。〕"
    "《僧祇律》中，首先說明五種正食。鈔文所說『同此』，是指同於《十誦律》；"
    "但《僧祇律》所說的是：麨（糗）、熟飯、麥飯、魚、肉。"
    "《僧祇律》中本來沒有乾飯，鈔文卻說與《十誦律》相同，"
    "這是因為《僧祇律》的麥飯正相當於《十誦律》五似食中的麥類之故。"
    "其次說明五種雜正食〔也就是不正食〕，與《四分律》相同，所以引來互相參照。"
    "佉闍尼，這裡翻譯為不正食。〔對照上面的《十誦律》，「枝」就是指莖，"
    "這裡沒有那裡的根，那裡也沒有這裡的花。〕"
)

# extra appended chars at seg end (closing bracket) for 10a#11
APPEND = {
    ("資持記", "10a_中三下", 11): "〕",
}

rows = []
for key in KEYS:
    book, chunk, seg = key
    segs = load(book, chunk)
    cur = segs[seg - 1]
    if key == ("資持記", "10a_中三下", 7):
        new = SEG7
    else:
        new = cur
        for old, rep in REPL[key]:
            n = new.count(old)
            if n != 1:
                raise SystemExit("MATCH FAIL %s old=%r count=%d" % (key, old, n))
            new = new.replace(old, rep)
        if key in APPEND:
            new = new + APPEND[key]
    # sanity: no newline / tab
    assert "\n" not in new and "\t" not in new, key
    rows.append((book, chunk, seg, new, cur))

with open(OUTTSV, "w", encoding="utf-8", newline="\n") as f:
    for book, chunk, seg, new, cur in rows:
        f.write("%s\t%s\t%d\t%s\n" % (book, chunk, seg, new))

print("rows=%d" % len(rows))
for book, chunk, seg, new, cur in rows:
    print("%s/%s#%d len %d -> %d changed=%s" % (book, chunk, seg, len(cur), len(new), new != cur))
