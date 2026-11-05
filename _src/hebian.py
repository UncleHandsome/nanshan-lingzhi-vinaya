
# -*- coding: utf-8 -*-
import io, os, re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
def cn(n):
    d='〇一二三四五六七八九'
    if n<10: return d[n]
    if n<20: return '十'+(d[n%10] if n%10 else '')
    return d[n//10]+'十'+(d[n%10] if n%10 else '')
FONT='DFKai-SB'; LATIN='Times New Roman'
def set_run(r,size,bold=False,color=None):
    r.font.size=Pt(size); r.font.bold=bold; r.font.name=LATIN
    rPr=r._element.get_or_add_rPr(); rf=rPr.find(qn('w:rFonts'))
    if rf is None: rf=OxmlElement('w:rFonts'); rPr.append(rf)
    rf.set(qn('w:ascii'),LATIN); rf.set(qn('w:hAnsi'),LATIN); rf.set(qn('w:eastAsia'),FONT)
    if color is not None: r.font.color.rgb=color
def shade(p,c):
    pPr=p._p.get_or_add_pPr(); shd=OxmlElement('w:shd'); shd.set(qn('w:val'),'clear'); shd.set(qn('w:color'),'auto'); shd.set(qn('w:fill'),c); pPr.append(shd)

def load(src, tr):
    S=os.path.join(D,'TXT_分卷',src); T=os.path.join(D,'AI語譯','out',tr)
    out=[]
    for f in sorted(os.listdir(S), key=lambda x:(0 if x.startswith('00_') else 1,x)):
        if not f.endswith('.txt'): continue
        key=f[:-4]; tp=os.path.join(T,key+'.txt')
        if not os.path.exists(tp): continue
        sp=[x.strip() for x in io.open(os.path.join(S,f),encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tt=[x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp,encoding='utf-8').read()) if x.strip()]
        out.append((key,sp,tt))
    return out

# 鈔：切篇（只取第一次出現的 30 篇）
cs=load('01_行事鈔','01_行事鈔')
cs_sec=[]; seen=set(); cur=None
for key,sp,tp in cs:
    for i in range(min(len(sp),len(tp))):
        m=re.match(r'^([\u4e00-\u9fff]{2,8})篇第([一二三四五六七八九十]+)$', sp[i])
        if m and m.group(1) not in seen:
            seen.add(m.group(1)); cur=dict(name=m.group(1), items=[(sp[i],tp[i])]); cs_sec.append(cur)
        elif cur is not None:
            cur['items'].append((sp[i],tp[i]))
print('鈔篇', len(cs_sec), [s['name'] for s in cs_sec][:5])

# 記：切科判
zj=load('資持記_細分','資持記')
zj_sec=[]; cur=None
for key,sp,tp in zj:
    for i in range(min(len(sp),len(tp))):
        m=re.search(r'釋([\u4e00-\u9fff]{2,6})篇', tp[i]) or re.search(r'釋([\u4e00-\u9fff]{2,6})篇', sp[i])
        if m:
            cur=dict(name=m.group(1), items=[(sp[i],tp[i])]); zj_sec.append(cur)
        elif cur is not None:
            cur['items'].append((sp[i],tp[i]))
print('記段', len(zj_sec))

MAP = [('標宗顯德','點明宗旨'),('集僧通局','集僧'),('足數眾相','足數'),('受欲是非','受欲'),('通辨羯磨','羯磨'),
       ('結界方法','結界'),('僧網大綱','僧網'),('受戒緣集','受戒'),('師資相攝','師資'),('說戒正儀','說戒'),
       ('安居策修','安居'),('自恣宗要','自恣'),('篇聚名報','篇聚'),('隨戒釋相','戒相'),('持犯方軌','持犯'),
       ('懺六聚法','懺六聚法'),('二衣總別','二衣'),('四藥受淨','四藥'),('鉢器制聽','鉢器'),('對施興治','對施'),
       ('頭陀行儀','頭陀'),('僧像致敬','僧像致敬'),('訃請設則','赴請'),('導俗化方','導俗'),('主客相待','主客'),
       ('瞻病送終','瞻病'),('諸雜要行','諸雜'),('沙彌別法','沙彌'),('尼眾別行','尼眾'),('諸部別行','諸部律')]
def build(vol_name, n_from, n_to):
    doc=Document(); st=doc.styles['Normal']; st.font.size=Pt(11); st.font.name=LATIN
    st.element.rPr.rFonts.set(qn('w:eastAsia'),FONT)
    s=doc.sections[0]; s.page_width=Cm(21); s.page_height=Cm(29.7)
    s.top_margin=Cm(1.7); s.bottom_margin=Cm(1.6); s.left_margin=Cm(1.8); s.right_margin=Cm(1.8)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    set_run(p.add_run('四分律行事鈔資持記合編'), 20, bold=True)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(16)
    set_run(p.add_run(vol_name + '（鈔文・記文對照）'), 12, color=RGBColor(0x66,0x66,0x66))
    for idx in range(n_from-1, min(n_to, len(cs_sec))):
        sec = cs_sec[idx]; zname = MAP[idx][1] if idx < len(MAP) else ''
        p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        pf=p.paragraph_format; pf.space_before=Pt(18); pf.space_after=Pt(4); pf.page_break_before=(idx>n_from-1)
        set_run(p.add_run('第%s篇　%s' % (cn(idx+1), sec['name'])), 15, bold=True)
        p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(8)
        set_run(p.add_run('【鈔】'), 10, bold=True, color=RGBColor(0x8a,0x4a,0x1f))
        for o,t in sec['items']:
            q=doc.add_paragraph(); qf=q.paragraph_format
            qf.left_indent=Pt(6); qf.space_before=Pt(4); qf.space_after=Pt(0); qf.line_spacing=1.25; qf.keep_with_next=True
            set_run(q.add_run(o), 10, color=RGBColor(0x6b,0x5b,0x4a)); shade(q,'F4EFE2')
            a=doc.add_paragraph(); a.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
            af=a.paragraph_format; af.first_line_indent=Pt(22); af.line_spacing=1.4; af.space_before=Pt(1); af.space_after=Pt(4)
            set_run(a.add_run(t), 11)
        # 記
        items=[]
        if zname:
            for z in zj_sec:
                if z['name']==zname: items += z['items']
        if items:
            p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(10); p.paragraph_format.space_after=Pt(4)
            set_run(p.add_run('【記】'+ ('　' + zname + '篇' if zname else '')), 10, bold=True, color=RGBColor(0x21,0x5a,0x8a))
            for o,t in items:
                q=doc.add_paragraph(); qf=q.paragraph_format
                qf.left_indent=Pt(6); qf.space_before=Pt(4); qf.space_after=Pt(0); qf.line_spacing=1.25; qf.keep_with_next=True
                set_run(q.add_run(o), 10, color=RGBColor(0x6b,0x5b,0x4a)); shade(q,'EEF2F6')
                a=doc.add_paragraph(); a.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
                af=a.paragraph_format; af.first_line_indent=Pt(22); af.line_spacing=1.4; af.space_before=Pt(1); af.space_after=Pt(4)
                set_run(a.add_run(t), 11)
    out=os.path.join(D,'白話','行事鈔資持記合編_%s.docx' % vol_name)
    doc.save(out); print(vol_name, 'saved', len(doc.paragraphs))

build('上卷', 1, 12)
build('中卷', 13, 16)
build('下卷', 17, 30)
