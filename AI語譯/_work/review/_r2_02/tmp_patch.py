# -*- coding: utf-8 -*-
import io
p="_r2b.py"; s=io.open(p,encoding="utf-8").read()
old='''            for mm in re.finditer(r"(\\d{3})-(\\d{4})", b):
                k = mm.group(1) + "-" + mm.group(2)
                if k in d and d[k][0].split("/")[1] == chunk:
                    segs.append(d[k][1])
            if not segs:'''
new='''            for mm in re.finditer(r"(\\d{3})-(\\d{4})", b):
                k = mm.group(1) + "-" + mm.group(2)
                if k in d and d[k][0].split("/")[1] == chunk:
                    segs.append(d[k][1])
            if not segs:
                for mm in re.finditer(r"【(\\d{4})】", b):
                    k = str(n) + "-" + mm.group(1)
                    if k in d and d[k][0].split("/")[1] == chunk:
                        segs.append(d[k][1])
            if not segs:
                for mm in re.finditer(r"(?<![\\d-])(\\d{4})(?![\\d-])", b):
                    k = str(n) + "-" + mm.group(1)
                    if k in d and d[k][0].split("/")[1] == chunk:
                        segs.append(d[k][1])
            if not segs:'''
assert old in s
s=s.replace(old,new)
io.open(p,"w",encoding="utf-8").write(s)
print("patched")
