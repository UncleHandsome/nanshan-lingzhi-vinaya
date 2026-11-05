
# -*- coding: utf-8 -*-
import io, os, re, json, bisect
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
VAR = {'牀':'床','説':'說','衆':'眾','爲':'為','敎':'教','卽':'即','旣':'既','竝':'並'}
def nh(ch): return VAR.get(ch, ch)
def ishan(ch): return '\u4e00' <= ch <= '\u9fff' or ch == '〇'
S = os.path.join(D,'TXT_分卷','03_業疏'); T = os.path.join(D,'AI語譯','out','03_業疏')
files = sorted([f for f in os.listdir(S) if f.endswith('.txt')], key=lambda x: (0 if x.startswith('00_') else 1, x))
src_lines=[]; tr=[]
for f in files:
    key=f[:-4]
    sp=[x.strip() for x in io.open(os.path.join(S,f),encoding='utf-8').read().split('\n')[5:] if x.strip()]
    tp=[x.strip() for x in re.split(r'\n\s*\n', io.open(os.path.join(T,key+'.txt'),encoding='utf-8').read()) if x.strip()]
    for i in range(min(len(sp),len(tp))):
        src_lines.append(sp[i]); tr.append(tp[i])
src=''.join(nh(c) for c in ''.join(src_lines) if ishan(c))
line_start=[]; off=0
for l in src_lines:
    h=''.join(nh(c) for c in l if ishan(c)); line_start.append(off); off+=len(h)
line_end = line_start[1:] + [len(src)]
ju_raw=io.open(os.path.join(D,'03_四分律刪補隨機羯磨疏_句讀_clean.txt'),encoding='utf-8').read()
ju_paras=[p.strip() for p in re.split(r'\n\s*\n', ju_raw) if p.strip()]
ju=''.join(nh(c) for c in ju_raw if ishan(c))
para_start=[]; off=0
for p in ju_paras:
    h=''.join(nh(c) for c in p if ishan(c)); para_start.append(off); off+=len(h)
para_end = para_start[1:] + [len(ju)]

anchors = json.load(io.open(os.path.join(D,'AI語譯','_work','ys_anchors.json'),encoding='utf-8'))
ap = [a for a,_ in anchors]; aq = [b for _,b in anchors]
def ju_to_src(pos):
    i = bisect.bisect_right(aq, pos) - 1
    if i < 0: return max(0, pos)
    return ap[i] + (pos - aq[i])
# 每行譯文歸給「重疊最多」的句讀段
buckets = [[] for _ in ju_paras]
for li in range(len(src_lines)):
    s, e = line_start[li], line_end[li]
    if e <= s: continue
    # 該行在 ju 的大致位置
    jp = None
    i = bisect.bisect_right(ap, s) - 1
    if i >= 0: jp = aq[i] + (s - ap[i])
    if jp is None: continue
    # 找包含 jp 的段
    pi = bisect.bisect_right(para_start, jp) - 1
    pi = max(0, min(pi, len(ju_paras)-1))
    buckets[pi].append(li)
FONT='DFKai-SB'; LATIN='Times New Roman'
def set_run(r,size,bold=False,color=None):
    r.font.size=Pt(size); r.font.bold=bold; r.font.name=LATIN
    rPr=r._element.get_or_add_rPr(); rf=rPr.find(qn('w:rFonts'))
    if rf is None: rf=OxmlElement('w:rFonts'); rPr.append(rf)
    rf.set(qn('w:ascii'),LATIN); rf.set(qn('w:hAnsi'),LATIN); rf.set(qn('w:eastAsia'),FONT)
    if color is not None: r.font.color.rgb=color
def shade(p,c):
    pPr=p._p.get_or_add_pPr(); shd=OxmlElement('w:shd'); shd.set(qn('w:val'),'clear'); shd.set(qn('w:color'),'auto'); shd.set(qn('w:fill'),c); pPr.append(shd)
doc=Document(); st=doc.styles['Normal']; st.font.size=Pt(11); st.font.name=LATIN
st.element.rPr.rFonts.set(qn('w:eastAsia'),FONT)
sec=doc.sections[0]; sec.page_width=Cm(21); sec.page_height=Cm(29.7)
sec.top_margin=Cm(1.7); sec.bottom_margin=Cm(1.6); sec.left_margin=Cm(1.8); sec.right_margin=Cm(1.8)
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
set_run(p.add_run('四分律刪補隨機羯磨疏'), 22, bold=True)
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after=Pt(6)
set_run(p.add_run('句讀原文・白話對照'), 13, color=RGBColor(0x66,0x66,0x66))
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after=Pt(20)
set_run(p.add_run('唐·道宣律師疏／宋·元照律師記　·　句讀原文與白話逐段對照'), 9.5, color=RGBColor(0x88,0x88,0x88))
for pi, txt in enumerate(ju_paras):
    q=doc.add_paragraph(); qf=q.paragraph_format
    qf.left_indent=Pt(6); qf.space_before=Pt(6); qf.space_after=Pt(0); qf.line_spacing=1.35; qf.keep_with_next=(len(txt) < 90)
    set_run(q.add_run(txt), 11, color=RGBColor(0x5f,0x4e,0x3c)); shade(q,'F6F1E6')
    lis = buckets[pi]
    if lis:
        body = '　'.join(tr[li] for li in lis)
        a=doc.add_paragraph(); a.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
        af=a.paragraph_format; af.first_line_indent=Pt(24); af.line_spacing=1.5; af.space_before=Pt(3); af.space_after=Pt(6)
        set_run(a.add_run(body), 12)
out=os.path.join(D,'白話','業疏_句讀對照本.docx')
doc.save(out)
print('paras', len(ju_paras), 'with-trans', sum(1 for b in buckets if b), 'saved')
