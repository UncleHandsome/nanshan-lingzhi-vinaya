
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


# 鈔：依分卷（01a_卷上之一 → 卷上之一）串接，篇名標記
cs=load('01_行事鈔','01_行事鈔')
flat=[]
vols=[]
for k,sp,tt in cs:
    vol=k.split('_',1)[1] if '_' in k else k
    if vol not in vols: vols.append(vol)
    for i in range(len(sp)):
        flat.append((sp[i], tt[i] if i < len(tt) else '', vol))
PATS=re.compile(r'^([\u4e00-\u9fff]{2,8})篇第([一二三四五六七八九十]+)$')
secs=[]; cur=None
for o,t,vol in flat:
    m=PATS.match(o)
    if m:
        if any(x['no']==m.group(2) for x in secs):
            cur=next(x for x in secs if x['no']==m.group(2))
        else:
            cur=dict(name=m.group(1), no=m.group(2), items=[]); secs.append(cur)
    if cur is not None: cur['items'].append((o,t,vol))
print('CSSEC', len(secs), 'VOLS', len(vols))

# 記
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


# 記文分節（34 節）→ 鈔篇（30 篇）的對應；師資、戒相、篇首數節為多節併一篇
Z2S = [0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 8, 9, 10, 11, 12, 13, 13, 13,
       14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]


RE_SLICE = True
_ZI = {}


def _build_zi():
    for idx in range(30):
        _ZI[idx] = []
    for i, sec in enumerate(zsecs):
        if i < len(Z2S):
            _ZI[Z2S[i]] += sec['items']
    # 依人工診斷重切：篇14 前 122 段實為篇13 的記文
    if RE_SLICE and len(_ZI[13]) > 122:
        _ZI[12] = _ZI[12] + _ZI[13][:122]
        _ZI[13] = _ZI[13][122:]
    # 篇12 最後一段是中卷卷頭題記，應歸篇13
    if RE_SLICE and len(_ZI[11]) > 90:
        _ZI[12] = [_ZI[11][-1]] + _ZI[12]
        _ZI[11] = _ZI[11][:-1]


def zitems_for(idx):
    if not _ZI:
        _build_zi()
    return _ZI.get(idx, [])


def _old_zitems_for(idx):
    out = []
    for zi, sec in enumerate(zsecs):
        if zi < len(Z2S) and Z2S[zi] == idx:
            out += sec['items']
    return out


import json as _json
AIMAP = {}
try:
    AIMAP = _json.load(io.open(os.path.join(D, 'AI語譯', '_work', 'hb_align.json'), encoding='utf-8'))
    print('AI 對齊表：篇', len(AIMAP), '記段', sum(len(v) for v in AIMAP.values()))
except Exception as _e:
    print('no AIMAP', _e)

SKIP1=re.compile(r'^\d+\s*[\u4e00-\u9fff]{2,10}篇\(上[一二三四五六七八九十]?\)$')
SKIP2=re.compile(r'^[\u4e00-\u9fff]{2,10}篇第[一二三四五六七八九十]+$')

# 先為每一篇算好記文分配
PLAN=[]
for idx,sec in enumerate(secs):
    zi=zitems_for(idx)
    anchors={}
    for k,(zo,zt) in enumerate(zi):
        for q in re.findall(r'「([^」]{12,})」', zo):
            qh=han(q)[:12]
            if len(qh)<12: continue
            for ci,(co,ct,_v) in enumerate(sec['items']):
                if qh in han(co):
                    anchors.setdefault(ci,[]).append(k); break
    am = AIMAP.get(str(idx))
    front = []
    if am:
        # c 是「已濾掉標題行」的鈔段序號；0 代表篇前總釋
        valid = [i for i, (o, t, *_) in enumerate(sec['items'])
                 if not SKIP1.match(o.strip()) and not SKIP2.match(o.strip())]
        anchors = {}
        lastc = valid[0] if valid else 0
        for k in range(len(zi)):
            if k < len(am):
                c = max(0, int(am[k]))
                if c == 0 and k < len(am):
                    front.append(k)
                    continue
                if valid:
                    c = valid[min(c - 1 if c > 0 else 0, len(valid) - 1)]
                lastc = min(len(sec['items']) - 1, c)
            anchors.setdefault(lastc, []).append(k)
        used = set(range(len(zi)))
    used=set(v for vs in anchors.values() for v in vs)
    n_i=max(1,len(sec['items']))
    clen=[max(1,len(han(o))) for o,t,*_ in sec['items']]
    total_c=float(sum(clen)); edges=[]; acc=0.0
    for L in clen:
        edges.append((acc/total_c,(acc+L)/total_c)); acc+=L
    zlen=[max(1,len(han(o))) for o,t in zi]
    total_z=float(sum(zlen)) if zi else 1.0
    accz=0.0
    for k in range(len(zi)):
        mid=(accz+zlen[k]/2.0)/total_z
        accz+=zlen[k]
        if k in used: continue
        ci=n_i-1
        for j,(a,b) in enumerate(edges):
            if a<=mid<b:
                ci=j; break
        anchors.setdefault(ci,[]).append(k)
    # 把落在「標題行」上的記段改掛到最近的有效鈔段，避免漏印
    valid = [i for i, (o, t, *_ ) in enumerate(sec['items'])
             if not SKIP1.match(o.strip()) and not SKIP2.match(o.strip())]
    if valid:
        for ci in list(anchors):
            if ci in valid:
                continue
            ks = anchors.pop(ci)
            nxt = next((v for v in valid if v > ci), valid[-1])
            anchors.setdefault(nxt, []).extend(ks)
    PLAN.append((idx, zi, anchors, front))


def build(label, vol):
    doc=Document(); st=doc.styles['Normal']; st.font.size=Pt(10); st.font.name=LATIN
    st.element.rPr.rFonts.set(qn('w:eastAsia'),FONT)
    s=doc.sections[0]; s.page_width=Cm(21); s.page_height=Cm(29.7)
    s.top_margin=Cm(1.6); s.bottom_margin=Cm(1.5); s.left_margin=Cm(1.8); s.right_margin=Cm(1.8)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    sr(p.add_run('行事鈔・資持記　句級合編'), 19, bold=True)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(14)
    sr(p.add_run(label), 11, color=RGBColor(0x66,0x66,0x66))
    n_sec=0
    for idx, zi, anchors, front in PLAN:
        sec=secs[idx]
        idxs=[i for i,(o,t,v) in enumerate(sec['items']) if v==vol and not SKIP1.match(o.strip()) and not SKIP2.match(o.strip())]
        if not idxs: continue
        n_sec+=1
        p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        pf=p.paragraph_format; pf.space_before=Pt(14); pf.space_after=Pt(6)
        first_all = min([i for i, (o, t, v) in enumerate(sec['items'])
                        if not SKIP1.match(o.strip()) and not SKIP2.match(o.strip())] or [0])
        tail=('（續）' if min(idxs) > first_all else '')
        sr(p.add_run('第%d篇　%s%s' % (idx+1, sec['name'], tail)), 14, bold=True)
        for k in front:
            zo, zt = zi[k]
            r=doc.add_paragraph(); rf=r.paragraph_format
            rf.space_before=Pt(4); rf.space_after=Pt(0); rf.line_spacing=1.2; rf.keep_with_next=True
            sr(r.add_run('【記】'+zo), 9.5, color=RGBColor(0x21,0x5a,0x8a)); shade(r,'EEF2F6')
            b2=doc.add_paragraph(); b2.alignment=WD_ALIGN_PARAGRAPH.LEFT
            bf=b2.paragraph_format; bf.first_line_indent=Pt(20); bf.line_spacing=1.35; bf.space_after=Pt(2)
            sr(b2.add_run(zt), 10.5)
        for ci in idxs:
            co,ct,_v=sec['items'][ci]
            q=doc.add_paragraph(); qf=q.paragraph_format
            qf.space_before=Pt(7); qf.space_after=Pt(0); qf.line_spacing=1.2; qf.keep_with_next=True
            sr(q.add_run('【鈔】'+co), 9.5, color=RGBColor(0x6b,0x5b,0x4a)); shade(q,'F4EFE2')
            a2=doc.add_paragraph(); a2.alignment=WD_ALIGN_PARAGRAPH.LEFT
            af=a2.paragraph_format; af.first_line_indent=Pt(20); af.line_spacing=1.35; af.space_after=Pt(2)
            sr(a2.add_run(ct), 10.5)
            for k in sorted(anchors.get(ci,[])):
                zo,zt=zi[k]
                r=doc.add_paragraph(); rf=r.paragraph_format
                rf.space_before=Pt(4); rf.space_after=Pt(0); rf.line_spacing=1.2; rf.left_indent=Pt(14); rf.keep_with_next=True
                sr(r.add_run('【記】'+zo), 9.5, color=RGBColor(0x21,0x5a,0x8a)); shade(r,'EEF2F6')
                b2=doc.add_paragraph(); b2.alignment=WD_ALIGN_PARAGRAPH.LEFT
                bf=b2.paragraph_format; bf.first_line_indent=Pt(20); bf.line_spacing=1.35; bf.space_after=Pt(2); bf.left_indent=Pt(14)
                sr(b2.add_run(zt), 10.5)
    out=os.path.join(D,'白話','行事鈔資持記句級合編_%s.docx' % label)
    doc.save(out)
    print('%s saved %d 篇 %d paras' % (label, n_sec, len(doc.paragraphs)))


for v in vols:
    build(v, v)
