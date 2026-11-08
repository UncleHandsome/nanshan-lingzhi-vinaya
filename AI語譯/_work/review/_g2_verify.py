import json, io, importlib.util
spec = importlib.util.spec_from_file_location('ap','AI語譯/_work/review/_g2_apply.py')
# instead of importing (it writes), re-read data
rows=json.load(io.open('AI語譯/_work/review/_g2_rows.json',encoding='utf-8'))
lines=io.open('AI語譯/_work/review/fix_re2_g2.tsv',encoding='utf-8').read().split('\n')
lines=[l for l in lines if l]
print('out rows',len(lines))
bad=[i for i,l in enumerate(lines) if len(l.split('\t'))!=4]
print('bad cols',bad)
# duplicates identical?
from collections import defaultdict
g=defaultdict(list)
for l in lines:
    f=l.split('\t'); g[(f[1],f[2])].append(f[3])
for k,v in g.items():
    if len(v)>1:
        print('dup',k,'identical=',len(set(v))==1)
# leading quote check
for d in rows:
    if d['current'][:1]=='"': print('leading quote idx',d['idx'])
