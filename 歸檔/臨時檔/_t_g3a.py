import io, sys, os
sys.stdout.reconfigure(encoding="utf-8")
lines=[l for l in io.open(r"AI語譯\_work\review\fix_re8_g3.tsv",encoding="utf-8").read().split("\n") if l.strip()]
for l in lines:
    f=l.split("\t")
    if f[0]=="資持記" and f[1]=="11d_中四上" and f[2] in ("12","13","14","15"):
        print(f[1],f[2],"len",len(f[3]))
        print(repr(f[3][:150]))
        print("  has newline?", "\n" in f[3])
