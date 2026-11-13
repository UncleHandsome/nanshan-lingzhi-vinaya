# -*- coding: utf-8 -*-
"""合併 _7kv_new.json→_7kv_edits.json、_7kv_jnew.json→_7kv_judge.json，並印出統計。"""
import os, json, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def merge(new, dst):
    np, dp = os.path.join(HERE, new), os.path.join(HERE, dst)
    if not os.path.exists(np):
        return 0
    b = json.load(open(np, encoding="utf-8"))
    a = json.load(open(dp, encoding="utf-8")) if os.path.exists(dp) else []
    a += b
    json.dump(a, open(dp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.remove(np)
    return len(b)


ne = merge("_7kv_new.json", "_7kv_edits.json")
nj = merge("_7kv_jnew.json", "_7kv_judge.json")
print("merged edits", ne, "judge", nj)
judge = json.load(open(os.path.join(HERE, "_7kv_judge.json"), encoding="utf-8"))
from collections import Counter
print("judge total", len(judge), Counter(x["v"] for x in judge))
print("files", len(set(x["f"] for x in judge)))
