import json
d=json.load(open(r"AI語譯\_work\review\_re8g1_ext2.json",encoding="utf-8"))
ls=[l for l in open(r"AI語譯\out\03_業疏\15b_卷三之四.txt",encoding="utf-8").read().split("\n") if l.strip()]
x=[y for y in d if y["gid"]=="559-0008"][0]
print("BOOK[35]:",ls[35])
print()
print("CUR    :",x["CUR"])
