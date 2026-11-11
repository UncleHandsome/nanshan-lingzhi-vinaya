# -*- coding: utf-8 -*-
import io
p="_mat.py"; s=io.open(p,encoding="utf-8").read()
old='''        n, s = pair.split(":")
        n = int(n); s = int(s)
        d = PER[str(n)]
        chunk = None
        for k, v in d.items():
            if v[1] == s:
                chunk = v[0].split("/")[1]
                break'''
new='''        d = None
        if ":" in pair:
            n, s = pair.split(":")
            n = int(n); s = int(s)
            d = PER[str(n)]
            chunk = None
            for k, v in d.items():
                if v[1] == s:
                    chunk = v[0].split("/")[1]
                    break
        else:
            key = pair.split("-")[0].lstrip("0") if False else pair
            k3, k4 = pair.split("-")
            n = int(k3); key = k3.zfill(3) + "-" + k4
            d = PER[str(n)]
            chunk = d[key][0].split("/")[1]
            s = d[key][1]'''
assert old in s
s=s.replace(old,new)
io.open(p,"w",encoding="utf-8").write(s)
print("ok")
