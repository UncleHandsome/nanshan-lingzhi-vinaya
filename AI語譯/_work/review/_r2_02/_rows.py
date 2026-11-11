# -*- coding: utf-8 -*-
"""Row-level claim table with better ID attribution."""
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

def bare_at(txt, pre, idx, budget=30):
    """bare 4-digit near start or in 【】/「」quotes at start"""
    out=[]
    for m in re.finditer(r"(?<!\d)(\d{4})(?!\d)",txt):
        if m.start()>budget and "【" not in txt[max(0,m.start()-3):m.start()]: continue
        g="%s-%s"%(pre,m.group(1))
        if g in idx and g not in out: out.append(g)
    return out

def lead_ids(line, pre, idx):
    """IDs in the leading cell / heading area of a line."""
    s=line.strip()
    s=re.sub(r"^\|\s*","",s)
    head=s[:40]
    out=[]
    for m in ID_FULL.finditer(head):
        g=m.group(1)+"-"+m.group(2)
        if g in idx and g not in out: out.append(g)
    if not out: out=bare_at(head,pre,idx,budget=14)
    return out

def split_rows(b):
    lines=[l for l in b.split("\n")]
    if sum(1 for l in lines if l.strip().startswith("|"))>=2:
        rows=[l for l in lines if l.strip().startswith("|")]
        rows=[r for r in rows if not re.match(r"^\|[\s\-:|]+\|?$",r.strip())]
        if rows and re.search(r"原譯|問題|建議|段\b", rows[0]): rows=rows[1:]
        return [("ROW",r) for r in rows]
    cur=[]; out=[]
    for l in lines:
        if re.match(r"^\s*(?:[-*•]|\d+[.、)])\s", l) and cur:
            out.append(("LINE","\n".join(cur))); cur=[l]
        else: cur.append(l)
    if cur: out.append(("LINE","\n".join(cur)))
    return out

def main():
    idx=L.load_map()["idx"]
    rows=[]
    for n in resp_nums():
        t=io.open(os.path.join(ROOT,"batch_qwen","r2","resp_%d.txt"%n),encoding="utf-8-sig").read()
        for bi,b in enumerate(blocks(t)):
            summ=bool(SUMMARY.search(b[:30]))
            for kind,unit in split_rows(b):
                ids=lead_ids(unit,n,idx)
                if not ids:
                    allf=[m.group(1)+"-"+m.group(2) for m in ID_FULL.finditer(unit)]
                    allf=[g for g in allf if g in idx]
                    if len(set(allf))==1: ids=[allf[0]]
                if not ids: continue
                txt=re.sub(r"\s+"," ",unit).strip()
                rows.append({"resp":n,"bi":bi,"kind":kind,"ids":ids,"text":txt,
                             "claim":bool(CLAIM.search(txt)),
                             "neg":bool(NEG.search(txt)) and not re.search(r"建議|應作|宜改|改為|問題",txt),
                             "summ":summ})
    # keep only claims
    rows=[r for r in rows if r["claim"] and not r["neg"]]
    for i,r in enumerate(rows): r["cid"]="C%d-%d"%(r["resp"],r["bi"])
    json.dump(rows,io.open(os.path.join(OUT,"_claims.json"),"w",encoding="utf-8"),ensure_ascii=False)
    print("claim rows:",len(rows),"chars:",sum(len(r["text"]) for r in rows))
    c=collections.Counter(r["resp"] for r in rows)
    print("per-file avg:", round(len(rows)/len(c),1), "max:", c.most_common(3))
    print("multi-id rows:",sum(1 for r in rows if len(r["ids"])>1),"summary rows:",sum(1 for r in rows if r["summ"]))

if __name__=="__main__": main()
