# -*- coding: utf-8 -*-
"""Section-level claim table: heading + its bullets = one claim; tables split per row."""
import os, re, io, json, sys, collections
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
sys.path.insert(0, OUT)
import _r2lib as L

ID_FULL=re.compile(r"(?<!\d)(\d{3})-(\d{4})(?!\d)")
NEG=re.compile(r"無誤|無問題|正確|妥當|無需|不必|不需|均可|皆可|無礙|允當|貼切|精準|未見問題|沒有問題|無須")
CLAIM=re.compile(r"問題|建議|應作|宜作|宜改|改為|改作|誤|漏|增譯|脫|應是|不當|不符|矛盾|相反|顛倒|生硬|可作|不妥|欠|缺|錯|混|失|費解|難懂|不統一|不一致|歧義|贅|多餘|語病|搭配|不通|未譯|查無|無據")
SUMMARY=re.compile(r"最該改|總計|總結|優先|以上|合計|總共|先改")

def resp_nums():
    d=os.path.join(ROOT,"batch_qwen","r2"); out=[]
    for f in os.listdir(d):
        m=re.match(r"resp_(\d+)\.txt$",f)
        if m and 550<=int(m.group(1))<=641: out.append(int(m.group(1)))
    return sorted(out)

def blocks(t): return [b.strip() for b in re.split(r"\n\s*\n", t) if b.strip()]

def ids_in(txt, pre, idx, head=None, budget=14):
    out=[]; s=re.sub(r"^\|\s*","",txt.strip())
    scope=s[:head] if head else s
    for m in ID_FULL.finditer(scope):
        g=m.group(1)+"-"+m.group(2)
        if g in idx and g not in out: out.append(g)
    if not out:
        for m in re.finditer(r"(?<!\d)(\d{4})(?!\d)",scope):
            if m.start()>budget and "【" not in scope[max(0,m.start()-3):m.start()]: continue
            g="%s-%s"%(pre,m.group(1))
            if g in idx and g not in out: out.append(g)
    return out

def main():
    idx=L.load_map()["idx"]
    claims=[]
    for n in resp_nums():
        t=io.open(os.path.join(ROOT,"batch_qwen","r2","resp_%d.txt"%n),encoding="utf-8-sig").read()
        for bi,b in enumerate(blocks(t)):
            lines=b.split("\n")
            cur=None; secs=[]
            for l in lines:
                if re.match(r"^\s*#{1,4}\s", l) or re.match(r"^\s*\*\*\d+[.、]", l) or re.match(r"^\s*\d+[.、]\s*\*\*", l):
                    cur={"h":l,"lines":[]}; secs.append(cur)
                else:
                    if cur is None: cur={"h":"","lines":[]}; secs.append(cur)
                    cur["lines"].append(l)
            blk_ids=ids_in(b,n,idx,head=None)  # full IDs anywhere in block
            for sec in secs:
                txt="\n".join([sec["h"]]+sec["lines"]).strip()
                if not txt: continue
                sids=ids_in(sec["h"],n,idx,head=60) or ids_in(txt,n,idx,head=45)
                rows=[l.strip() for l in sec["lines"] if l.strip().startswith("|")]
                if len(rows)>=2 and not sids:
                    hdr=[r for r in rows if re.search(r"原譯|問題|建議",r)]
                    body=[r for r in rows if r not in hdr and not re.match(r"^\|[\s\-:|]+\|?$",r)]
                    for r in body:
                        rid=ids_in(r,n,idx,head=40)
                        claims.append({"resp":n,"bi":bi,"ids":rid,"text":re.sub(r"\s+"," ",r).strip(),"summ":False})
                    continue
                if not sids:
                    sids=blk_ids if len(blk_ids)==1 else []
                    if not sids and len(blk_ids)>1:
                        # nearest: fall back to first full id of block if section tiny
                        sids=[]
                txt=re.sub(r"\s+"," ",txt).strip()
                claims.append({"resp":n,"bi":bi,"ids":sids,"text":txt,"summ":bool(SUMMARY.search(txt[:40]))})
    keep=[]
    for c in claims:
        if not c["ids"]: continue
        if not (CLAIM.search(c["text"]) and not (NEG.search(c["text"]) and not re.search(r"建議|應作|宜改|改為|問題",c["text"]))): continue
        keep.append(c)
    for i,c in enumerate(keep): c["cid"]="K%03d"%i
    json.dump(keep,io.open(os.path.join(OUT,"_claims2.json"),"w",encoding="utf-8"),ensure_ascii=False)
    print("claims:",len(keep),"chars:",sum(len(c["text"]) for c in keep))
    print("no-id dropped? total raw:",len(claims),"kept:",len(keep))
    print("multi-id:",sum(1 for c in keep if len(c["ids"])>1))
    ch=collections.Counter()
    for c in keep:
        for g in c["ids"]: ch[idx[g]["chunk"][:3]]+=1
    print(sorted(ch.items()))

if __name__=="__main__": main()
