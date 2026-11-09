import json
data=json.load(open("AI語譯/_work/review/tmp_re8/groups.json",encoding="utf-8"))
for i in (36,53):
    cur=data[i][1][0]["current"]
    print("====",i, data[i][0])
    print(repr(cur[:120]))
    print(repr(cur[-120:]))
cur=data[53][1][0]["current"]
j=cur.find("故」字以下")
print("IDX53:", repr(cur[max(0,j-30):j+40]))
print("count 「:", cur.count("「"), " 」:", cur.count("」"))
