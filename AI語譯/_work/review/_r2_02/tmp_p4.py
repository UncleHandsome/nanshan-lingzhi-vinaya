# -*- coding: utf-8 -*-
import io
s=io.open("_r2b.py",encoding="utf-8").read()
s=s.replace("def build(tok, topn=6, cl=205, pl=210","def build(tok, topn=5, cl=195, pl=195")
s=s.replace('for sc, n, b in unlocated[:5]','for sc, n, b in unlocated[:3]')
s=s.replace('re.sub(r"\\s+", " ", b)[:90]','re.sub(r"\\s+", " ", b)[:80]')
io.open("_r2b.py","w",encoding="utf-8").write(s)
print("ok")
