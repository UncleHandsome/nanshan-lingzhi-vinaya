# -*- coding: utf-8 -*-
import csv, io, os
p = r"AI語譯/_work/review/fix_t1pack.tsv"
raw = open(p,"rb").read()
print("BOM:", raw[:3]==b"\xef\xbb\xbf", "CRLF:", raw.count(b"\r\n"), "LF:", raw.count(b"\n"), "bytes:", len(raw))
lines = raw.decode("utf-8").split("\n")
if lines and lines[-1]=="": lines=lines[:-1]
print("lines:", len(lines))
bad=0
for i,l in enumerate(lines,1):
    f=l.split("\t")
    if len(f)!=4: print("BAD COLS", i, len(f)); bad+=1
    if any(x=="" for x in f): print("EMPTY", i); bad+=1
    if "\r" in l: print("CR", i); bad+=1
print("bad:", bad)

# compare to report current and live
raw2 = open(r"AI語譯/_work/review/report_t1pack.tsv",encoding="utf-8-sig").read()
R = list(csv.reader(io.StringIO(raw2), delimiter="\t"))[1:]
def paras(book,chunk):
    t=open(f"AI語譯/out/{book}/{chunk}.txt",encoding="utf-8-sig").read().replace("\r\n","\n")
    return [x for x in t.split("\n\n") if x.strip()]
assert len(lines)==len(R)==69
ch=0
for i,(l,r) in enumerate(zip(lines,R)):
    book,chunk,seg,new=l.split("\t")
    assert (book,chunk,seg)==(r[0],r[1],r[2]), (i,book,chunk,seg)
    cur=r[9].replace("\n","")
    live=paras(book,chunk)[int(seg)-1].replace("\n","")
    if cur!=live: print("STALE",i+1)
    if new!=cur: ch+=1
    if new==cur:
        assert new==live, (i+1,"noop but differs from live")
print("changed rows:", ch)
# uniqueness of keys
keys=[tuple(l.split("\t")[:3]) for l in lines]
print("unique keys:", len(set(keys)))
