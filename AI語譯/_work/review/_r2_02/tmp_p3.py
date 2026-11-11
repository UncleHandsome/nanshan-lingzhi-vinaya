# -*- coding: utf-8 -*-
import io
s=io.open("_r2b.py",encoding="utf-8").read()
s=s.replace("def build(tok, topn=8, cl=250, pl=300","def build(tok, topn=6, cl=205, pl=210")
io.open("_r2b.py","w",encoding="utf-8").write(s)
print("ok")
