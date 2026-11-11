# -*- coding: utf-8 -*-
import json, io, os
ROOT=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
O=os.path.join(ROOT,"AI語譯","_work","review","_r2_02")
M=json.load(io.open(os.path.join(O,"_map.json"),encoding="utf-8"))
print("map keys", list(M.keys()))
print("idx len", len(M["idx"]))
k=list(M["idx"])[0]
print("idx sample", k, {kk:(str(vv)[:60]) for kk,vv in M["idx"][k].items()})
R=json.load(io.open(os.path.join(O,"_refs.json"),encoding="utf-8"))
print("refs keys", list(R.keys()))
print("by_chunk n", len(R["by_chunk"]))
print("sample", list(R["by_chunk"].items())[:2])
