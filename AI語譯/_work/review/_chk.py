import io,sys
sys.path.insert(0,r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review")
from _rv_kit import read_chunk
for ch in ["11a_卷三上之二","11b_卷三上之二","11c_卷三上之二"]:
    raw,eol,lines,idxs,p=read_chunk(ch)
    bad=0
    for i in idxs:
        s=lines[i]
        for a,b in [("「","」"),("『","』"),("（","）"),("〔","〕")]:
            if s.count(a)!=s.count(b):
                bad+=1; print("UNBAL",ch,i+1,a,b,s.count(a),s.count(b))
    print(ch,"lines",len(idxs),"bad",bad,"crlf",("\r" in raw))
