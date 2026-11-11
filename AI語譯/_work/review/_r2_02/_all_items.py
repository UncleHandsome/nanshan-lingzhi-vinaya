# -*- coding: utf-8 -*-
"""Parse ALL resp_550..641 into structured items, grouped by chunk/seg."""
import os, re, io, json, sys, collections
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
sys.path.insert(0, OUT)
import _r2lib as L

def pres_range(a=550,b=641):
    got=[]
    for n in range(a,b+1):
        p=os.path.join(ROOT,"batch_qwen","r2","resp_%d.txt"%n)
        if os.path.exists(p): got.append(n)
    return got

HDR = re.compile(r"^#{1,4}\s*(\d{3})-(\d{4})")
def parse_file(n):
    p=os.path.join(ROOT,"batch_qwen","r2","resp_%d.txt"%n)
    t=io.open(p,encoding="utf-8-sig").read()
    lines=t.split("\n")
    items=[]; cur=None
    pre=None
    for ln in lines:
        m=HDR.match(ln.strip())
        if m:
            if cur: items.append(cur)
            g=m.group(1)+"-"+m.group(2)
            cur={"resp":n,"g":g,"hdr":ln.strip(),"lines":[]}
            continue
        if cur is not None:
            cur["lines"].append(ln)
    if cur: items.append(cur)
    # non-item tail text (prose) not attached
    for it in items:
        body="\n".join(it["lines"]).strip()
        it["body"]=body
        pm=re.match(r"^#{1,4}\s*\S*?(\d{3}-\d{4})\s*[｜|]\s*([^｜|]*)[｜|]\s*(P\d)?[｜|]?\s*(.*)$", it["hdr"])
        it["prio"]=(pm.group(3) if pm and pm.group(3) else "")
        it["typ"]=(pm.group(4).strip() if pm and pm.group(4) else "")
        it["src"]=(pm.group(2).strip() if pm else "")
    return t, items

def main():
    M=L.load_map(); idx=M["idx"]
    allitems=[]; stats={}
    for n in pres_range():
        t,items=parse_file(n)
        stats[n]={"bytes":len(t),"items":len(items)}
        for it in items:
            g=it["g"]
            if g not in idx:
                it["chunk"]=None; it["seg"]=None
            else:
                it["chunk"]=idx[g]["chunk"]; it["seg"]=int(idx[g]["seg"])
            allitems.append(it)
    json.dump(allitems, io.open(os.path.join(OUT,"_all_items.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
    tot=len(allitems)
    print("total items:", tot)
    print("unlocatable:", sum(1 for x in allitems if not x.get("chunk")))
    bych=collections.Counter(x["chunk"] for x in allitems if x.get("chunk"))
    for k,v in sorted(bych.items(), key=lambda z:str(z[0])): print(k,v)
    print("files with 0 items:", [n for n,v in stats.items() if v["items"]==0])

if __name__=="__main__": main()
