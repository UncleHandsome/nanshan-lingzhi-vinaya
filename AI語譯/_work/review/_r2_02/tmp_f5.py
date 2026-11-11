# -*- coding: utf-8 -*-
import io
p="ops_17c.json"; s=io.open(p,encoding="utf-8").read()
s=s.replace("17c_卷四上之三","17c_卷四上之二")
io.open(p,"w",encoding="utf-8").write(s)
print("fixed")
