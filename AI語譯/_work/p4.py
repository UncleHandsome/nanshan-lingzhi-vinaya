import json,os,sys
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
km=json.load(open(r"AI語譯\_work\keymap.json",encoding="utf-8"))
for k in ["370-0004","015-0004","08b_卷中之四-06","09b_卷二下之二-06","05a_卷中之一-10","05a_卷中之一-11","09a_卷下之一-04","116-0002（別界住處）","116-0002（兩無任得）","259-0001 (1)","259-0001 (2)","459-0009（兩舌戒野干）","459-0009（二房戒龍鳥）"]:
    print(k, "->", km.get(k))
