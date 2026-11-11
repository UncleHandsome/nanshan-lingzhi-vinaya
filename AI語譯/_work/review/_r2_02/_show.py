# -*- coding: utf-8 -*-
"""Show segments -> utf8 file. python _show.py <chunk> <segs> [outfile]"""
import os, sys, io
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
sys.path.insert(0, OUT)
import _r2lib as L

def main():
    ch=sys.argv[1]; segs=[int(x) for x in sys.argv[2].replace(" ","").split(",") if x]
    out=sys.argv[3] if len(sys.argv)>3 else os.path.join(OUT,"show_%s.txt"%ch[:3])
    idx=L.load_map()["idx"]; ps=L.paras(ch)
    rev={int(e["seg"]):g for g,e in idx.items() if e["chunk"]==ch}
    Ls=[]
    for s in segs:
        Ls.append("\n===== #%d %s"%(s,rev.get(s,"?")))
        if not (0<s<=len(ps)): Ls.append("OUT OF RANGE"); continue
        Ls.append("原: "+idx[rev[s]]["orig"])
        Ls.append("譯: "+ps[s-1])
    io.open(out,"w",encoding="utf-8").write("\n".join(Ls))
    print("wrote",out)

if __name__=="__main__": main()
