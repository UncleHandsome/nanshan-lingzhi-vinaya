
# -*- coding: utf-8 -*-
import io, os, re
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
def load_pairs(src_dir, tr_dir):
    S=os.path.join(D,'TXT_分卷',src_dir); T=os.path.join(D,'AI語譯','out',tr_dir)
    out=[]
    for f in sorted(os.listdir(S)):
        if not f.endswith('.txt'): continue
        key=f[:-4]
        tpath=os.path.join(T,key+'.txt')
        if not os.path.exists(tpath): continue
        sp=[x.strip() for x in io.open(os.path.join(S,f),encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tp=[x.strip() for x in re.split(r'\n\s*\n', io.open(tpath,encoding='utf-8').read()) if x.strip()]
        out.append((key, sp, tp))
    return out
cs = load_pairs('01_行事鈔','01_行事鈔')
zj = load_pairs('資持記_細分','資持記')
# 鈔：以「XX篇第N」切篇
cs_sections = []
cur = None
for key, sp, tp in cs:
    for i in range(min(len(sp), len(tp))):
        m = re.search(r'([\u4e00-\u9fff]{2,8})篇第([一二三四五六七八九十]+)', sp[i])
        if m and len(sp[i]) < 30:
            cur = dict(name=m.group(1), no=m.group(2), key=key, items=[])
            cs_sections.append(cur)
        if cur is None:
            cur = dict(name='序', no='0', key=key, items=[]); cs_sections.append(cur)
        cur['items'].append((sp[i], tp[i]))
# 記：以「釋XX篇」切
zj_sections = []
cur = None
for key, sp, tp in zj:
    for i in range(min(len(sp), len(tp))):
        m = re.search(r'釋([\u4e00-\u9fff]{2,6})篇', tp[i]) or re.search(r'釋([\u4e00-\u9fff]{2,6})篇', sp[i])
        if m:
            cur = dict(name=m.group(1), key=key, items=[])
            zj_sections.append(cur)
        if cur is not None:
            cur['items'].append((sp[i], tp[i]))
print('鈔篇', len(cs_sections), [s['name'] for s in cs_sections][:8])
print('記篇', len(zj_sections), [s['name'] for s in zj_sections][:8])
import json
json.dump(dict(cs=[(s['name'], s['no'], len(s['items'])) for s in cs_sections],
               zj=[(s['name'], len(s['items'])) for s in zj_sections]),
          io.open(os.path.join(D,'AI語譯','_work','hebian_sections.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)
