
# -*- coding: utf-8 -*-
import io, os, re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
FONT='DFKai-SB'; LATIN='Times New Roman'
def sr(r,size,bold=False,color=None):
    r.font.size=Pt(size); r.font.bold=bold; r.font.name=LATIN
    rPr=r._element.get_or_add_rPr(); rf=rPr.find(qn('w:rFonts'))
    if rf is None: rf=OxmlElement('w:rFonts'); rPr.append(rf)
    rf.set(qn('w:ascii'),LATIN); rf.set(qn('w:hAnsi'),LATIN); rf.set(qn('w:eastAsia'),FONT)
    if color is not None: r.font.color.rgb=color
def shade(p,c):
    pPr=p._p.get_or_add_pPr(); shd=OxmlElement('w:shd'); shd.set(qn('w:val'),'clear'); shd.set(qn('w:color'),'auto'); shd.set(qn('w:fill'),c); pPr.append(shd)
def load(src,tr):
    S=os.path.join(D,'TXT_分卷',src); T=os.path.join(D,'AI語譯','out',tr); out=[]
    for f in sorted(os.listdir(S), key=lambda x:(0 if x.startswith('00_') else 1,x)):
        if not f.endswith('.txt'): continue
        k=f[:-4]; tp=os.path.join(T,k+'.txt')
        if not os.path.exists(tp): continue
        sp=[x.strip() for x in io.open(os.path.join(S,f),encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tt=[x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp,encoding='utf-8').read()) if x.strip()]
        out.append((k,sp,tt))
    return out
cs=load('01_行事鈔','01_行事鈔')
# 取「標宗顯德」篇
sec=[]; cur=None
for k,sp,tt in cs:
    for i in range(min(len(sp),len(tt))):
        if re.match(r'^[\u4e00-\u9fff]{2,8}篇第[一二三四五六七八九十]+$', sp[i]):
            if cur: break
            cur=(sp[i],[])
        if cur: cur[1].append((sp[i],tt[i]))
    if cur: break
print('鈔段', len(cur[1]))
# 記：取點明宗旨篇
zj=load('資持記_細分','資持記')
zsec=[]; cur2=None
for k,sp,tt in zj:
    for i in range(min(len(sp),len(tt))):
        m=re.search(r'釋([\u4e00-\u9fff]{2,6})篇', tt[i]) or re.search(r'釋([\u4e00-\u9fff]{2,6})篇', sp[i])
        if m: cur2=(m.group(1),[]); zsec.append(cur2)
        if cur2: cur2[1].append((sp[i],tt[i]))
zj_items=[]
for name,items in zsec:
    if name=='點明宗旨': zj_items += items
print('記段', len(zj_items))
# A: 引文錨定
cs_h=[''.join(re.findall(r'[\u4e00-\u9fff]',o)) for o,_ in cur[1]]
anchor={}
for zi,(zo,zt) in enumerate(zj_items):
    for q in re.findall(r'「([^」]{12,})」', zo):
        qh=''.join(re.findall(r'[\u4e00-\u9fff]',q))
        if len(qh)<12: continue
        for ci,ch in enumerate(cs_h):
            if qh[:12] in ch:
                anchor.setdefault(ci,[]).append(zi); break
print('錨定鈔段', len(anchor), '記段', sum(len(v) for v in anchor.values()))
# C: 其餘按比例
used=set(z for v in anchor.values() for z in v)
rest=[i for i in range(len(zj_items)) if i not in used]
if rest:
    step=max(1,len(zj_items)//len(cur[1]) or 1)
    for ci in range(len(cur[1])):
        if ci in anchor: continue
        k=ci*len(zj_items)//len(cur[1])
        if k in used: continue
        anchor.setdefault(ci,[]).append(k); used.add(k)
doc=Document(); st=doc.styles['Normal']; st.font.size=Pt(10); st.font.name=LATIN
st.element.rPr.rFonts.set(qn('w:eastAsia'),FONT)
s=doc.sections[0]; s.page_width=Cm(21); s.page_height=Cm(29.7)
s.top_margin=Cm(1.6); s.bottom_margin=Cm(1.5); s.left_margin=Cm(1.8); s.right_margin=Cm(1.8)
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
sr(p.add_run('行事鈔・資持記　句級合編（樣張）'), 18, bold=True)
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(14)
sr(p.add_run('第1篇 標宗顯德　／　記 點明宗旨'), 11, color=RGBColor(0x66,0x66,0x66))
for ci,(co,ct) in enumerate(cur[1]):
    q=doc.add_paragraph(); q.paragraph_format.space_before=Pt(8); q.paragraph_format.space_after=Pt(0); q.paragraph_format.line_spacing=1.2
    q.paragraph_format.keep_with_next=True
    sr(q.add_run('【鈔】'+co), 9.5, color=RGBColor(0x6b,0x5b,0x4a)); shade(q,'F4EFE2')
    a=doc.add_paragraph(); a.paragraph_format.first_line_indent=Pt(20); a.paragraph_format.line_spacing=1.35; a.paragraph_format.space_after=Pt(2)
    a.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY; sr(a.add_run(ct), 10.5)
    for zi in anchor.get(ci,[]):
        zo,zt=zj_items[zi]
        r=doc.add_paragraph(); r.paragraph_format.space_before=Pt(4); r.paragraph_format.space_after=Pt(0); r.paragraph_format.line_spacing=1.2
        r.paragraph_format.keep_with_next=True; r.paragraph_format.left_indent=Pt(14)
        sr(r.add_run('【記】'+zo), 9.5, color=RGBColor(0x21,0x5a,0x8a)); shade(r,'EEF2F6')
        b=doc.add_paragraph(); b.paragraph_format.first_line_indent=Pt(20); b.paragraph_format.line_spacing=1.35; b.paragraph_format.space_after=Pt(2); b.paragraph_format.left_indent=Pt(14)
        b.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY; sr(b.add_run(zt), 10.5)
out=os.path.join(D,'白話','合編樣張_標宗顯德.docx')
doc.save(out); print('saved', out)
