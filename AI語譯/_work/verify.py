import os,sys,glob,re,collections
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
best={}
for bk in sorted(glob.glob(r"歸檔\存疑套用前\*\*.txt")):
    rel=bk.split("存疑套用前\\")[1]
    book,fn=rel.split("\\")
    base=re.sub(r'_\d+(?=\.txt$)','',fn)
    key=(book,base)
    # 取最先（無後綴）者為批次前基準
    if key not in best or fn==base: best[key]=(bk,fn==base)
ok=True; tot=0
for (book,fn),(bk,isbase) in sorted(best.items()):
    cur=os.path.join("AI語譯","out",book,fn)
    if not os.path.exists(cur): print("MISSING OUT",cur); ok=False; continue
    a=open(bk,encoding="utf-8",newline="").read(); b=open(cur,encoding="utf-8",newline="").read()
    la,lb=a.split("\n"),b.split("\n")
    assert len(la)==len(lb),(fn,len(la),len(lb))
    diffs=[i for i in range(len(la)) if la[i]!=lb[i]]
    paras=[i//2+1 for i in diffs]
    tot+=len(diffs)
    print(f'{book}/{fn:<26} base={isbase} changed={len(diffs):<2} paras={paras} CRLF {a.count(chr(13)+chr(10))}->{b.count(chr(13)+chr(10))} LF {a.count(chr(10))}->{b.count(chr(10))}')
    if a.count("\n")!=b.count("\n") or a.count("\r\n")!=b.count("\r\n"): print("  !! EOL"); ok=False
    if any(i%2 for i in diffs): print("  !! odd line"); ok=False
print("files:",len(best),"changed paragraphs:",tot,"ALL OK" if ok else "PROBLEMS")
