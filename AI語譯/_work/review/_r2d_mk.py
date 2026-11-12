# -*- coding: utf-8 -*-
"""通用：讀 _r2d_items_<n>.json 產生 edits_<n>.json。
json: {"n":1588,"items":[[seq,old,new,why],...],"verdicts":[...]}"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2d_build as B

d = json.load(open(sys.argv[1], encoding='utf-8-sig'))
B.make(int(d['n']), [tuple(x) for x in d['items']], d.get('verdicts', []))
