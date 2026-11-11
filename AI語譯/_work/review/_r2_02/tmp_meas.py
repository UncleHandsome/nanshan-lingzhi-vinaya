# -*- coding: utf-8 -*-
import io, os, re, glob, collections, json
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"; R2=os.path.join(ROOT,"batch_qwen","r2")
nums=[n for n in sorted(int(re.search(r"resp_(\d+)",p).group(1)) for p in glob.glob(os.path.join(R2,"resp_*.txt"))) if 642<=n<=876]
STRONG=re.compile(r"相反|顛倒|譯反|主詞|受詞|施受|應作|誤譯|譯錯|讀成|當成|當作|混為|矛盾|不成詞|非是|不是.{1,12}而是|錯解|誤解|丟了|脫落|方向|說反|變成.{1,6}義|失準|曲解|誤|錯|漏|增")
tot=0; strong=0; blocks=0; sblocks=0
for n in nums:
    t=io.open(os.path.join(R2,"resp_%d.txt"%n),encoding="utf-8-sig",errors="replace").read()
    tot+=len(t)
    bs=[b.strip() for b in re.split(r"\n\s*\n",t) if b.strip()]
    blocks+=len(bs)
    for b in bs:
        if STRONG.search(b):
            strong+=len(b); sblocks+=1
print("files",len(nums),"chars",tot,"blocks",blocks,"strong chars",strong,"%d%%"%(100*strong/tot),"strong blocks",sblocks)
