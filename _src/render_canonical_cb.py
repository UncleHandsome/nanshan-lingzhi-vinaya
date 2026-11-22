# -*- coding: utf-8 -*-
"""依 CBETA 卷題切頁，不用 row 的 vol 過濾；跨頁 row 以重疊方式選入。"""
import argparse, io, json, os, re, html
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
C = os.path.join(B, '定稿')
BOOKS = {
 'xingshichao': ('行事鈔', 'TXT/01_四分律刪繁補闕行事鈔.txt', ('卷上','卷中','卷下'), r'【四分律刪繁補闕行事鈔(卷[上中下](?:之[一二三四])?)】'),
 'jieshu': ('戒疏', 'TXT/02_四分律含注戒本疏.txt', ('卷一','卷二','卷三','卷四'), r'【四分律含注戒本疏(?:行宗記)?(卷[一二三四](?:[上下])?之?[一二三四]?)】'),
 'yeshu': ('業疏', 'TXT/03_四分律刪補隨機羯磨疏.txt', ('卷一','卷二','卷三','卷四'), r'【四分律刪補隨機羯磨疏(?:濟緣記)?(卷[一二三四](?:之[一二三四])?)】'),
 'nicao': ('尼鈔', 'TXT/04_四分律比丘尼鈔.txt', ('卷上','卷中','卷下'), r'【四分律比丘尼鈔(卷[上中下](?:之[上中下])?)】'),
 'yichao': ('義鈔', 'TXT/05_四分律拾毗尼義鈔.txt', ('卷上','卷中'), r'【四分律拾毗尼義鈔(卷[上中下](?:之[一二三四])?)】'),
}
def norm(v):
 m=re.match(r'卷([上中下]|[一二三四])',v); return '卷'+m.group(1) if m else v
PUNCT = re.compile(r'[，。；：！？、]')
def fmt(s):
 s=html.escape(s)
 s=re.sub('\u3000{2,}','<br><br>',s)
 return s.replace('\n','<br>')
def pick(src, disp):
 return disp if disp and PUNCT.search(disp) else src
def pairs(row):
 segs=row.get('segments') or []
 if segs:
  return [(s.get('label') or '疏文',pick(s.get('source',''),s.get('display_source')),s.get('translation','')) for s in segs]
 return [(row.get('label') or '疏文',pick(row.get('source',''),row.get('display_source')),row.get('translation',''))]
ap=argparse.ArgumentParser(); ap.add_argument('--book',choices=sorted(BOOKS)); args=ap.parse_args()
for book in ([args.book] if args.book else list(BOOKS)):
 name,rawp,vols,pat=BOOKS[book]
 raw=io.open(os.path.join(B,rawp),encoding='utf-8').read()
 hpos=[0]*(len(raw)+1); _c=0
 for _i,_ch in enumerate(raw):
  if '\u4e00'<=_ch<='\u9fff': _c+=1
  hpos[_i+1]=_c
 marks=[(hpos[m.start()],norm(m.group(1)),m.group(1)) for m in re.finditer(pat,raw)]
 starts={}
 for pos,v,txt in marks:
  starts.setdefault(v,pos)
 order=[v for v in vols if v in starts]
 intervals=[]
 for i,v in enumerate(order):
  a=starts[v]; b=starts[order[i+1]] if i+1<len(order) else len(raw)
  intervals.append((v,a,b))
 if intervals: intervals[0]=(intervals[0][0],0,intervals[0][2])
 rows=[json.loads(x) for x in io.open(os.path.join(C,book+'.jsonl'),encoding='utf-8') if x.strip()]
 rows=[r for r in rows if r.get('raw_start',-1)>=0]
 rows.sort(key=lambda r:(r['raw_start'],r['raw_end']))
 for v,a,b in intervals:
  sel=[r for r in rows if r['raw_start']<b and r['raw_end']>a]
  body=['<h1>%s・%s</h1>'%(name,v),'<p class="byline">%d 單元；依 CBETA 卷題區間，跨頁單元前後並見。</p>'%len(sel)]
  idx=0; last=None
  for r in sel:
   chunk=r.get('chunk') or v
   if chunk!=last:
    idx+=1; body.append('<h2 class="sec" id="p%d">%s</h2>'%(idx,html.escape(chunk))); last=chunk
   for lab,s,tr in pairs(r):
    if not s or not tr: continue
    pc={'疏文':'s','記文':'j','註文':'z','律文':'lv','序文':'x'}.get(lab,'')
    oc={'疏文':'shu','記文':'ji','註文':'zhu','律文':'lv','序文':'xu'}.get(lab,'')
    ld='' if book=='nicao' else '【%s】'%lab
    body.append('<div class="pair %s"><div class="o %s">%s%s</div><div class="t">%s%s</div></div>'%(pc,oc,ld,fmt(s),ld,fmt(tr)))
  p=os.path.join(B,'docs',book,v+'.html'); t=io.open(p,encoding='utf-8').read(); m=re.search(r'<main id="main">.*?</main>',t,re.S)
  new=t[:m.start()]+'<main id="main">'+''.join(body)+'</main>'+t[m.end():]
  io.open(p+'.new','w',encoding='utf-8').write(new)
  print(name,v,'pairs',sum(1 for r in sel for _ in pairs(r)),'->',p+'.new')
