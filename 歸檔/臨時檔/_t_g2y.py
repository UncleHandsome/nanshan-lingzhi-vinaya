import io, sys, os
sys.stdout.reconfigure(encoding="utf-8")
base=r"AI語譯\out\03_業疏"
txt=io.open(os.path.join(base,"03a_卷一之三.txt"),encoding="utf-8").read().replace("\r\n","\n")
bl=[b.strip() for b in txt.split("\n\n") if b.strip()]
src=bl[68]
out=io.open(r"AI語譯\_work\review\fix_re8_g1.tsv",encoding="utf-8").read().split("\n")[0].split("\t")[3]
print("SRC len",len(src),"newline?", "\n" in src, "first80:",repr(src[:80]))
print("OUT len",len(out),"first80:",repr(out[:80]))
print("equal?", src==out)
# find first difference
for i,(a,b) in enumerate(zip(src,out)):
    if a!=b:
        print("diff at",i,repr(src[i-20:i+40]),"|",repr(out[i-20:i+40])); break
