# -*- coding: utf-8 -*-
"""Extract opinion blocks from resp_550..641; attach to segment IDs; dump per-chunk digest."""
import os, re, io, json, sys, collections
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
sys.path.insert(0, OUT)
import _r2lib as L

def resp_nums():
    d=os.path.join(ROOT,"batch_qwen","r2")
    out=[]
    for f in os.listdir(d):
        m=re.match(r"resp_(\d+)\.txt$",f)
        if m and 550<=int(m.group(1))<=641: out.append(int(m.group(1)))
    return sorted(out)

ID_FULL=re.compile(r"(?<!\d)(\d{3})-(\d{4})(?!\d)")

def load_map():
    M=L.load_map(); return M["idx"]

def blocks(t):
    # split on blank lines
    return [b.strip() for b in re.split(r"\n\s*\n", t) if b.strip()]

def find_ids(block, pre, idx):
    ids=[]
    for m in ID_FULL.finditer(block):
        g=m.group(1)+"-"+m.group(2)
        if g in idx and g not in ids: ids.append(g)
    if not ids:
        for m in re.finditer(r"(?<!\d)(\d{4})(?!\d)",block):
            g="%s-%s"%(pre,m.group(1))
            if g in idx and g not in ids: ids.append(g)
    return ids

def main():
    idx=load_map()
    allrows=[]
    stats=[]
    for n in resp_nums():
        p=os.path.join(ROOT,"batch_qwen","r2","resp_%d.txt"%n)
        t=io.open(p,encoding="utf-8-sig").read()
        bs=blocks(t)
        nid=0
        for i,b in enumerate(bs):
            ids=find_ids(b,n,idx)
            if ids: nid+=1
            allrows.append({"resp":n,"bi":i,"ids":ids,"chunk":(idx[ids[0]]["chunk"] if ids else None),"text":b})
        stats.append((n,len(bs),nid,sum(len(b["text"]) for b in allrows if b["resp"]==n)))
    json.dump(allrows,io.open(os.path.join(OUT,"_blocks_all.json"),"w",encoding="utf-8"),ensure_ascii=False)
    tot=sum(s[3] for s in stats)
    print("files",len(stats),"blocks",len(allrows),"chars",tot)
    print("blocks with ids",sum(1 for r in allrows if r["ids"]))
    print("chars in id-blocks",sum(len(r["text"]) for r in allrows if r["ids"]))
    print("chars in no-id blocks",sum(len(r["text"]) for r in allrows if not r["ids"]))
    for s in stats[:10]: print(s)

if __name__=="__main__": main()
