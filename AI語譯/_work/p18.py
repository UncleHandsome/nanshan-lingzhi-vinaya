import json,sys,os
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
w={ (r["base"],r["book"],r["chunk"],r["found"]):r for r in json.load(open(r"AI語譯\_work\work2.json",encoding="utf-8")) }
def seg(key, needle, before=80, after=120, nth=0):
    r=w[key]; t=r["cur"]; i=-1
    for _ in range(nth+1): i=t.find(needle,i+1)
    print(f'{key[0]} #{key[3]} cls={r["cls"]}')
    print("  …"+t[max(0,i-before):i+after]+"…")
seg(("160-0005","01_行事鈔","07d_卷中之三",14),"不犯的情況",60,220)
seg(("484-0002","02_戒疏","06c_卷二上之二",108),"之戒福",60,40)
seg(("484-0002","02_戒疏","06c_卷二上之二",108),"之戒福",60,40,1)
seg(("224-0001","02_戒疏","05d_卷二上之一",94) if False else ("224-0001","01_行事鈔","10b_卷下之二",13),"樹上",50,60)
seg(("240-0003","01_行事鈔","11a_卷下之三",21),"接著先遞上水",40,120)
seg(("205-0002","01_行事鈔","09b_卷下之一",20),"自居",50,60)
seg(("241-0006","01_行事鈔","11a_卷下之三",27),"佛陀訓勉",60,90)
seg(("455-0011","02_戒疏","05d_卷二上之一",39),"最初的",30,80)
seg(("459-0004","02_戒疏","05d_卷二上之一",94),"第三",10,60)
seg(("459-0009","02_戒疏","05d_卷二上之一",99),"龍",30,140)
