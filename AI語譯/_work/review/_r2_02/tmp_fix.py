# -*- coding: utf-8 -*-
import io, re
p="_r2b.py"
s=io.open(p,encoding="utf-8").read()
s=s.replace('''def build(chunk, ctoks, topn=7, cl=210, pl=250, path=None):
    files=sorted(int(k) for k in PER if any(v[0].split("/")[1].startswith(chunk) for v in PER[k].values()))''',
'''def fullname(tok):
    names=set()
    for k in PER:
        for v in PER[k].values():
            nm=v[0].split("/")[1]
            if nm.split("_")[0]==tok: names.add(nm)
    assert len(names)==1, (tok,names)
    return names.pop()
def build(tok, ctoks=None, topn=7, cl=210, pl=250, path=None):
    chunk=fullname(tok)
    files=sorted(int(k) for k in PER if any(v[0].split("/")[1]==chunk for v in PER[k].values()))''')
s=s.replace('d[k][0].split("/")[1].split("_")[0]==chunk','d[k][0].split("/")[1]==chunk')
s=s.replace('v[0].split("/")[1].split("_")[0]==chunk','v[0].split("/")[1]==chunk')
s=s.replace('L.append("#### %s segs=%d files=%d claims=%d"%(chunk,','L.append("#### %s segs=%d files=%d claims=%d"%(tok,')
s=s.replace('p=path or ("dg_"+chunk+".txt")','p=path or ("dg_"+tok+".txt")')
io.open(p,"w",encoding="utf-8").write(s)
