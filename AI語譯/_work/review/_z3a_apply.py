# -*- coding: utf-8 -*-
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _z3a_lib import apply_edits

p = sys.argv[1]
data = json.load(open(p, encoding='utf-8'))
for chunk, edits in data.items():
    apply_edits(chunk, edits)
    print(chunk, len(edits), 'edits applied')
