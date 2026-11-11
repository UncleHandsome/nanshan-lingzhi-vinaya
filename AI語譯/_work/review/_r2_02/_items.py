# -*- coding: utf-8 -*-
"""Refine: split blocks into items (bullets / table rows / numbered paras), attach IDs."""
import os, re, io, json, sys, collections
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
sys.path.insert(0, OUT)
import _r2lib as L
ID_FULL=re.compile(r"(?<!\d)(\d{3})-(\d{4})(?!\d)")

def resp_nums():
    d=os.path.join(ROOT,"batch_qwen","r2")
    out=[]
    for f in os.listdir(d):
        m=re.match(r"resp_(\d+)\.txt$",f)
        if m and 550<=int(m.group(1))<=641: out.append(int(m.group(1)))
    return sorted(out)

def blocks(t):
    return [b.strip() for b in re.split(r"\n\s*\n", t) if b.strip()]

def ids_of(txt, pre, idx):
    out=[]
    for m in ID_FULL.finditer(txt):
        g=m.group(1)+"-"+m.group(2)
        if g in idx and g not in out: out.append(g)
    if not out:
        for m in re.finditer(r"(?<!\d)(\d{4})(?!\d)",txt):
            g="%s-%s"%(pre,m.group(1))
            if g in idx and g not in out: out.append(g)
    return out

def split_items(b, pre, idx):
    """Yield (ids, text) units."""
    lines=b.split("\n")
    # table?
    if sum(1 for l in lines if l.strip().startswith("|"))>=2:
        rows=[l for l in lines if l.strip().startswith("|")]
        # header rows
        hdr=rows[0] if rows else ""
        cur_ids=ids_of(b,pre,idx)
        if len(cur_ids)==1:
            yield cur_ids,b
            return
        for l in rows:
            if re.match(r"^\|[\s\-:|]+\|?$", l.strip()): continue
            row_ids=ids_of(l,pre,idx)
            yield (row_ids or cur_ids), l.strip()
        return
    # bullets / numbered
    cur=[]
    for l in lines:
        if re.match(r"^\s*(?:[-*•]|\d+[.、)]|（\d+）|\([0-9]+\))\s", l) and cur:
            yield ids_of("\n".join(cur),pre,idx) or ids_of(b,pre,idx), "\n".join(cur)
            cur=[l]
        else:
            cur.append(l)
    if cur:
        yield ids_of("\n".join(cur),pre,idx) or ids_of(b,pre,idx), "\n".join(cur)

CLAIM=re.compile(r"問題|建議|應作|宜作|宜改|改為|改作|誤|漏|增譯|脫|應是|不當|不符|矛盾|相反|顛倒|生硬|可作|不妥|欠|缺|錯|混|失|費解|難懂|不統一|不一致|歧義|贅|多餘|贅字|語病|搭配|不通|未譯|查無|無據|依據")

def main():
    idx=L.load_map()["idx"]
    rows=[]
    for n in resp_nums():
        p=os.path.join(ROOT,"batch_qwen","r2","resp_%d.txt"%n)
        t=io.open(p,encoding="utf-8-sig").read()
        for bi,b in enumerate(blocks(t)):
            for ids,txt in split_items(b,n,idx):
                if not ids: continue
                rows.append({"resp":n,"bi":bi,"ids":ids,"text":txt,"claim":bool(CLAIM.search(txt))})
    json.dump(rows,io.open(os.path.join(OUT,"_items_all.json"),"w",encoding="utf-8"),ensure_ascii=False)
    print("items:",len(rows),"claim items:",sum(1 for r in rows if r["claim"]))
    print("chars all:",sum(len(r["text"]) for r in rows),"chars claim:",sum(len(r["text"]) for r in rows if r["claim"]))
    # per chunk
    per=collections.defaultdict(lambda:[0,0,0,0])
    for r in rows:
        for g in r["ids"]:
            ch=idx[g]["chunk"]; k=ch[:3]
            per[k][0]+=1
            if r["claim"]: per[k][1]+=1
            per[k][2]+=len(r["text"])//max(1,len(r["ids"]))
            if r["claim"]: per[k][3]+=len(r["text"])//max(1,len(r["ids"]))
    for k in sorted(per): print(k,"items=%d claim=%d chars=%d claimchars=%d"%tuple(per[k]))

if __name__=="__main__": main()
