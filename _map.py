import re, os, json, unicodedata

BASE = r'.'
files = [181,188,192,226,277,392,413,441,448,472,473,475,477,479,480,481,551]

def parse_jiao(n):
    p = os.path.join('校閱_10K', f'校閱_{n:03d}.txt')
    s = open(p, encoding='utf-8-sig').read()
    segs = []
    for m in re.finditer(r'【(\d{3}-\d{4})】(\S+?)#(\d+)\r?\n【原文】(.*?)\r?\n【譯文】(.*?)(?=\r?\n\r?\n【|\Z)', s, re.S):
        segs.append(dict(id=m.group(1), src=m.group(2), para=int(m.group(3)),
                         src_text=m.group(4).strip(), trans=m.group(5).strip()))
    return segs

def paras(path):
    s = open(path, encoding='utf-8-sig').read()
    raw = s.splitlines()
    # paragraphs = blocks separated by blank lines
    blocks = []
    cur = []
    for l in raw:
        if l.strip() == '':
            if cur:
                blocks.append('\n'.join(cur)); cur=[]
        else:
            cur.append(l)
    if cur: blocks.append('\n'.join(cur))
    return blocks

# test 181
segs = parse_jiao(181)
print('181 segs', len(segs))
for sg in segs:
    print(sg['id'], sg['src'], sg['para'], len(sg['trans']))
b = paras(os.path.join('AI語譯','out','01_行事鈔','08a_卷中之四.txt'))
print('paras', len(b))
for sg in segs[:3]:
    cand = b[sg['para']-1]
    print('---', sg['id'], 'match=', cand.startswith(sg['trans'][:20]), 'len', len(cand), len(sg['trans']))
    print('CUR:', cand[:120])
    print('OLD:', sg['trans'][:120])
