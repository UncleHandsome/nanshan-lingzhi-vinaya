import io,os,json,sys
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT=os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
sys.path.insert(0,OUT)
import _r2lib as L
idx=L.load_map()["idx"]
chunks=["09b_卷二下之二","09c_卷二下之二","09d_卷二下之二","10a_卷三上之一","10b_卷三上之一","10c_卷三上之一","10d_卷三上之一","11a_卷三上之二","11b_卷三上之二","11c_卷三上之二","12a_卷三上之三","12b_卷三上之三"]
res=[]
for ch in chunks:
    raw=L.read_raw(ch)
    parts=raw.split("\r\n\r\n")
    n=len(parts)
    tail_empty = parts[-1]==""
    # seg count = n minus trailing empty
    segs = n-1 if tail_empty else n
    rev={int(e["seg"]):g for g,e in idx.items() if e["chunk"]==ch}
    # verify first/last orig prefix in paragraph
    ok=[]
    for s in (1,segs//2,segs):
        g=rev.get(s); p=parts[s-1] if s-1<len(parts) else ""
        ok.append((s, g, p.startswith("【")))
    res.append((ch,n,tail_empty,segs,ok))
for r in res: print(r[0], "parts=%d"%r[1], "tail=%s"%r[2], "segs=%d"%r[3], r[4])
