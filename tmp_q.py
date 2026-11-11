import io,os,sys
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT=os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
sys.path.insert(0,OUT)
import _r2lib as L
idx=L.load_map()["idx"]
for g in ["570-0001","578-0007","562-0002","553-0009","558-0007"]:
    print(g, idx.get(g,{}).get("chunk"), idx.get(g,{}).get("seg"))
