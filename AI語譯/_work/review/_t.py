import io,os,sys
sys.path.insert(0,r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review")
from _rv_dig2 import split_items
from _rv_kit import parse_x7
R=r"C:\Users\lionc\OneDrive\桌面\XW\三大部\batch_qwen\r7k"
for n in range(895,932):
    t=io.open(os.path.join(R,"resp_%d.txt"%n),encoding="utf-8").read()
    it=split_items(t)
    segs=parse_x7(str(n))
    print(n,"items=",len(it),"segs=",len(segs),"hdr=",[x[0] for x in it][:2])
