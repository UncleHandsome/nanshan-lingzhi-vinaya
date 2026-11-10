import re, io
p="_g2build.py"
s=io.open(p,encoding="utf-8").read()
s=s.replace("        29, 70}                                   # already covered by MAN below",
            "        29, 70, 47}                               # already covered by MAN below")
io.open(p,"w",encoding="utf-8").write(s)
print("patched")
