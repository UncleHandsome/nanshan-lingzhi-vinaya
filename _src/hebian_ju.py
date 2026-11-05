
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
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]', s))
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
# 鈔：所有段依序，篇名標記
cs=load('01_行事鈔','01_行事鈔')
flat=[]
for k,sp,tt in cs:
    for i in range(len(sp)):
        flat.append((sp[i], tt[i] if i < len(tt) else ''))
PATS=re.compile(r'^([\u4e00-\u9fff]{2,8})篇第([一二三四五六七八九十]+)$')
secs=[]; cur=None
for o,t in flat:
    m=PATS.match(o)
    if m:
        if any(x['no']==m.group(2) for x in secs):
            cur=next(x for x in secs if x['no']==m.group(2))
        else:
            cur=dict(name=m.group(1), no=m.group(2), items=[]); secs.append(cur)
    if cur is not None: cur['items'].append((o,t))
print('CSSEC', len(secs))
# 記：所有段依序，釋XX篇標記
zj=load('資持記_細分','資持記')
zflat=[]
for k,sp,tt in zj:
    for i in range(len(sp)):
        zflat.append((sp[i], tt[i] if i < len(tt) else ''))
ZP=re.compile(r'釋([\u4e00-\u9fff]{2,6})篇')
zsecs=[]; z=None
for o,t in zflat:
    m=ZP.search(t) or ZP.search(o)
    if m:
        z=dict(name=m.group(1), items=[]); zsecs.append(z)
    if z is not None: z['items'].append((o,t))
print('ZJSEC', len(zsecs))
MAP=[('標宗顯德','點明宗旨'),('集僧通局','集僧'),('足數眾相','足數'),('受欲是非','受欲'),('通辨羯磨','羯磨'),
     ('結界方法','結界'),('僧網大綱','僧網'),('受戒緣集','受戒'),('師資相攝','師資'),('說戒正儀','說戒'),
     ('安居策修','安居'),('自恣宗要','自恣'),('篇聚名報','篇聚'),('隨戒釋相','戒相'),('持犯方軌','持犯'),
     ('懺六聚法','懺六聚法'),('二衣總別','二衣'),('四藥受淨','四藥'),('鉢器制聽','鉢器'),('對施興治','對施'),
     ('頭陀行儀','頭陀'),('僧像致敬','僧像致敬'),('訃請設則','赴請'),('導俗化方','導俗'),('主客相待','主客'),
     ('瞻病送終','瞻病'),('諸雜要行','諸雜'),('沙彌別法','沙彌'),('尼眾別行','尼眾'),('諸部別行','諸部律')]
def zitems(zname):
    out=[]
    for s in zsecs:
        if s['name']==zname: out += s['items']
    return out
def build(label, a, b):
    doc=Document(); st=doc.styles['Normal']; st.font.size=Pt(10); st.font.name=LATIN
    st.element.rPr.rFonts.set(qn('w:eastAsia'),FONT)
    s=doc.sections[0]; s.page_width=Cm(21); s.page_height=Cm(29.7)
    s.top_margin=Cm(1.6); s.bottom_margin=Cm(1.5); s.left_margin=Cm(1.8); s.right_margin=Cm(1.8)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    sr(p.add_run('行事鈔・資持記　句級合編'), 19, bold=True)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(14)
    sr(p.add_run(label), 11, color=RGBColor(0x66,0x66,0x66))
    for idx in range(a-1, min(b, len(secs))):
        sec=secs[idx]; zname=MAP[idx][1] if idx < len(MAP) else ''
        p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        pf=p.paragraph_format; pf.space_before=Pt(14); pf.space_after=Pt(6)
        sr(p.add_run('第%d篇　%s' % (idx+1, sec['name'])), 14, bold=True)
        zi=zitems(zname)
        anchors={}
        for k,(zo,zt) in enumerate(zi):
            for q in re.findall(r'「([^」]{12,})」', zo):
                qh=han(q)[:12]
                if len(qh)<12: continue
                for ci,(co,ct) in enumerate(sec['items']):
                    if qh in han(co):
                        anchors.setdefault(ci,[]).append(k); break
        used=set(v for vs in anchors.values() for v in vs)
        # 其餘記文依前後比例分配到各鈔段之下（保持原順序），不再堆在篇首或篇末
        if zi:
            n_i = max(1, len(sec['items']))
            for k in range(len(zi)):
                if k in used:
                    continue
                ci = min(n_i - 1, k * n_i // max(1, len(zi)))
                anchors.setdefault(ci, []).append(k)
        for ci,(co,ct) in enumerate(sec['items']):
            # 首條若只是篇名標題（與上方篇名重複），略過
            if re.match(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇\(上[一二三四五六七八九十]?\)$', co.strip()):
                continue
            if re.match(r'^[\u4e00-\u9fff]{2,10}篇第[一二三四五六七八九十]+$', co.strip()):
                continue
            q=doc.add_paragraph(); qf=q.paragraph_format
            qf.space_before=Pt(7); qf.space_after=Pt(0); qf.line_spacing=1.2; qf.keep_with_next=True
            sr(q.add_run('【鈔】'+co), 9.5, color=RGBColor(0x6b,0x5b,0x4a)); shade(q,'F4EFE2')
            a2=doc.add_paragraph(); a2.alignment=WD_ALIGN_PARAGRAPH.LEFT
            af=a2.paragraph_format; af.first_line_indent=Pt(20); af.line_spacing=1.35; af.space_after=Pt(2)
            sr(a2.add_run(ct), 10.5)
            for k in anchors.get(ci,[]):
                zo,zt=zi[k]
                r=doc.add_paragraph(); rf=r.paragraph_format
                rf.space_before=Pt(4); rf.space_after=Pt(0); rf.line_spacing=1.2; rf.left_indent=Pt(14); rf.keep_with_next=True
                sr(r.add_run('【記】'+zo), 9.5, color=RGBColor(0x21,0x5a,0x8a)); shade(r,'EEF2F6')
                b2=doc.add_paragraph(); b2.alignment=WD_ALIGN_PARAGRAPH.LEFT
                bf=b2.paragraph_format; bf.first_line_indent=Pt(20); bf.line_spacing=1.35; bf.space_after=Pt(2); bf.left_indent=Pt(14)
                sr(b2.add_run(zt), 10.5)
    out=os.path.join(D,'白話','行事鈔資持記句級合編_%s.docx' % label)
    doc.save(out); print(label, 'paras', len(doc.paragraphs))
# 四冊：依《資持記》原書 16 卷，每 4 卷為一冊（與篇級合編同界線）
build('卷一',1,9)
build('卷二',10,13)
build('卷三',14,16)
build('卷四',17,30)
