
# -*- coding: utf-8 -*-
import io, os, re, json, bisect, sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
VAR = {'牀':'床','説':'說','衆':'眾','爲':'為','敎':'教','卽':'即','旣':'既','竝':'並'}
def nh(ch): return VAR.get(ch, ch)
def ishan(ch): return '\u4e00' <= ch <= '\u9fff' or ch == '〇'
def han(s): return ''.join(nh(c) for c in s if ishan(c))

def load(bookdir):
    S=os.path.join(D,'TXT_分卷',bookdir); T=os.path.join(D,'AI語譯','out',bookdir)
    files=sorted([f for f in os.listdir(S) if f.endswith('.txt')], key=lambda x:(0 if x.startswith('00_') else 1,x))
    lines=[]; trs=[]
    for f in files:
        key=f[:-4]
        sp=[x.strip() for x in io.open(os.path.join(S,f),encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tp=[x.strip() for x in re.split(r'\n\s*\n', io.open(os.path.join(T,key+'.txt'),encoding='utf-8').read()) if x.strip()]
        for i in range(min(len(sp),len(tp))):
            lines.append(sp[i]); trs.append(tp[i])
    return lines, trs

def ranges(items):
    starts=[]; off=0; hs=[]
    for it in items:
        h=han(it); hs.append(h); starts.append(off); off+=len(h)
    ends=starts[1:]+[off]
    return ''.join(hs), starts, ends

def anchors(a, b, K=20, STEP=40):
    out=[]
    for p in range(0, len(a)-K, STEP):
        seg=a[p:p+K]
        if len(set(seg))<8: continue
        q=b.find(seg)
        if q<0: continue
        if b.find(seg,q+1)>=0: continue
        out.append((p,q))
    return out

def build(bookdir, ju_path, title, outname):
    lines, trs = load(bookdir)
    src, ls, le = ranges(lines)
    ju_raw = io.open(ju_path, encoding='utf-8').read()
    raw_paras = [p.strip() for p in re.split(r'\n\s*\n', ju_raw) if p.strip()]
    # 顯示用：把長段按句切到 ~180 字
    paras = []
    for p0 in raw_paras:
        if len(p0) <= 220:
            paras.append(p0); continue
        buf = ''
        for s2 in re.findall(r'[^。！？]*[。！？]?', p0):
            if not s2: continue
            if len(buf) + len(s2) > 200 and buf:
                paras.append(buf); buf = s2
            else:
                buf += s2
        if buf.strip(): paras.append(buf)
    jus, ps, pe = ranges(paras)
    anc = anchors(jus, src)   # ju -> src
    ap=[x[0] for x in anc]; aq=[x[1] for x in anc]
    def ju2src(pos):
        i=bisect.bisect_right(ap,pos)-1
        if i<0: return max(0,pos)
        return aq[i]+(pos-ap[i])
    buckets=[[] for _ in paras]; nomatch=0
    for pi in range(len(paras)):
        sa, sb = ju2src(ps[pi]), ju2src(max(ps[pi]+1, pe[pi]-1))
        if sb <= sa: sb = sa + 1
        k0 = max(0, bisect.bisect_left(le, sa) - 1)
        got = []
        k = k0
        while k < len(lines) and ls[k] < sb:
            ov = min(le[k], sb) - max(ls[k], sa)
            if ov > 0.5 * (le[k] - ls[k]): got.append(k)
            k += 1
        buckets[pi] = got
        if not got: nomatch += 1
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
    s=doc.sections[0]; s.page_width=Cm(21); s.page_height=Cm(29.7)
    s.top_margin=Cm(1.7); s.bottom_margin=Cm(1.6); s.left_margin=Cm(1.8); s.right_margin=Cm(1.8)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    set_run(p.add_run(title), 20, bold=True)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after=Pt(18)
    set_run(p.add_run('句讀原文・白話對照'), 12, color=RGBColor(0x66,0x66,0x66))
    for pi, txt in enumerate(paras):
        q=doc.add_paragraph(); qf=q.paragraph_format
        qf.left_indent=Pt(6); qf.space_before=Pt(6); qf.space_after=Pt(0); qf.line_spacing=1.35; qf.keep_with_next=(len(txt)<90)
        set_run(q.add_run(txt), 11, color=RGBColor(0x5f,0x4e,0x3c)); shade(q,'F6F1E6')
        if buckets[pi]:
            body='　'.join(trs[k] for k in buckets[pi])
            a=doc.add_paragraph(); a.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
            af=a.paragraph_format; af.first_line_indent=Pt(24); af.line_spacing=1.5; af.space_before=Pt(3); af.space_after=Pt(6)
            set_run(a.add_run(body), 12)
    out=os.path.join(D,'白話',outname+'.docx')
    doc.save(out)
    print(outname,'paras',len(paras),'with-tr',sum(1 for b in buckets if b),'no-match',nomatch)

if __name__=='__main__':
    build('04_比丘尼鈔', os.path.join(D,'04_四分律比丘尼鈔_句讀_clean.txt'), '四分比丘尼鈔', '尼鈔_句讀對照本')
    build('05_拾毗尼義鈔', os.path.join(D,'05_四分律拾毗尼義鈔_句讀_clean.txt'), '四分律拾毗尼義鈔', '尼義鈔_句讀對照本')
