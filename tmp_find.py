import json
data=json.load(open("AI語譯/_work/review/tmp_re8/groups.json",encoding="utf-8"))
cur=data[25][1][0]["current"]
import re
for m in re.finditer("福報", cur):
    print(m.start(), repr(cur[max(0,m.start()-60):m.start()+60]))
print("---- tail ----")
print(repr(cur[-400:]))
