import io,os,re,sys,glob
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT=os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
chunks=["09b_卷二下之二","09c_卷二下之二","09d_卷二下之二","10a_卷三上之一","10b_卷三上之一","10c_卷三上之一","10d_卷三上之一","11a_卷三上之二","11b_卷三上之二","11c_卷三上之二","12a_卷三上之三","12b_卷三上之三"]
tot_claims=0
for ch in chunks:
    p=os.path.join(OUT,"q_%s.txt"%ch[:3])
    t=io.open(p,encoding="utf-8").read()
    n=len(re.findall(r"<K\d+@",t))
    tot_claims+=n
    print(ch[:3], n)
print("TOTAL claims",tot_claims)
