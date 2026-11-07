# -*- coding: utf-8 -*-
import csv, re, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base = r"AI語譯/_work/review/"
rows = list(csv.DictReader(open(base + "report_t2.tsv", encoding="utf-8-sig"), delimiter="\t"))
targets = ['02a_卷一上之二','02b_卷一上之二','02c_卷一上之二','05d_卷二上之一',
           '06a_卷二上之二','06c_卷二上之二','07a_卷二上之三','07b_卷二上之三']
sel = [r for r in rows if r['chunk'] in targets]
print("rows:", len(sel))

def load_in(chunk):
    p = base + "in/02_戒疏__" + chunk + ".txt"
    txt = open(p, encoding='utf-8').read()
    segs = {}
    for m in re.finditer(r'【段(\d{3})】(.*?)(?=【段\d{3}】|\Z)', txt, re.S):
        segs[int(m.group(1))] = m.group(2).strip()
    return segs

def load_out(chunk):
    p = "AI語譯/out/02_戒疏/" + chunk + ".txt"
    txt = open(p, encoding='utf-8').read()
    paras = [x for x in re.split(r'\r?\n\s*\r?\n', txt) if x.strip()]
    return paras

for r in sel:
    chunk, seg = r['chunk'], int(r['seg'])
    ins = load_in(chunk)
    outs = load_out(chunk)
    orig = r['orig']
    # find seg in 'in' whose souce part matches orig
    hits = []
    for k, v in ins.items():
        if orig.strip() and orig.strip() in v:
            hits.append(k)
    print("="*100)
    print(f"CHUNK {chunk} SEG {seg} status={r['status']} level={r['level']} cls={r['cls']}")
    print(f"  in_hits_for_orig={hits}  out_paras={len(outs)} in_paras={len(ins)}")
    print(f"  orig={orig[:60]}")
    print(f"  tr  ={r['tr'][:60]}")
    if 1 <= seg <= len(outs):
        print(f"  OUT[{seg}]={outs[seg-1][:80]}")
    for h in hits:
        if 1 <= h <= len(outs):
            print(f"  OUT[hit {h}]={outs[h-1][:80]}")
