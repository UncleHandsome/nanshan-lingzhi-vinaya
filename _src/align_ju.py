
# -*- coding: utf-8 -*-
import io, os, re, json
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(D,'TXT_分卷','03_業疏'); T = os.path.join(D,'AI語譯','out','03_業疏')
VAR = {'牀':'床','説':'說','衆':'眾','爲':'為','敎':'教','卽':'即','旣':'既','竝':'並'}
def nh(ch): return VAR.get(ch, ch)
def ishan(ch): return '\u4e00' <= ch <= '\u9fff' or ch == '〇'

files = sorted([f for f in os.listdir(S) if f.endswith('.txt')], key=lambda x: (0 if x.startswith('00_') else 1, x))
src_lines = []; tr_paras = []
for f in files:
    key = f[:-4]
    raw = io.open(os.path.join(S,f), encoding='utf-8').read().split('\n')[5:]
    sp = [x.strip() for x in raw if x.strip()]
    tp = [x.strip() for x in re.split(r'\n\s*\n', io.open(os.path.join(T,key+'.txt'), encoding='utf-8').read()) if x.strip()]
    n = min(len(sp), len(tp))
    for i in range(n):
        src_lines.append(sp[i]); tr_paras.append(tp[i])

src = ''.join(nh(c) for c in ''.join(src_lines) if ishan(c))
line_start = []; off = 0
for l in src_lines:
    h = ''.join(nh(c) for c in l if ishan(c))
    line_start.append(off); off += len(h)

ju_raw = io.open(os.path.join(D,'03_四分律刪補隨機羯磨疏_句讀_clean.txt'), encoding='utf-8').read()
ju_paras = [p.strip() for p in re.split(r'\n\s*\n', ju_raw) if p.strip()]
ju = ''.join(nh(c) for c in ju_raw if ishan(c))
para_start = []; off = 0
for p in ju_paras:
    h = ''.join(nh(c) for c in p if ishan(c))
    para_start.append(off); off += len(h)
print('src', len(src), 'ju', len(ju), 'lines', len(src_lines), 'paras', len(ju_paras))

# 貪婪對齊：src[i] ↔ ju[j]
m = {}
i = j = 0
while i < len(src) and j < len(ju):
    if src[i] == ju[j]:
        m[i] = j; i += 1; j += 1; continue
    # 嘗試重新同步：往後找 8 字相同的段落
    found = False
    for d in range(1, 6):
        if i+d < len(src) and src[i+d:i+d+8] and ju[j:j+8] and src[i+d:i+d+8] == ju[j:j+8]:
            i += d; found = True; break
        if j+d < len(ju) and src[i:i+8] and ju[j+d:j+d+8] and src[i:i+8] == ju[j+d:j+d+8]:
            j += d; found = True; break
    if not found:
        i += 1
print('aligned src chars', len(m))
json.dump(dict(lines=line_start, paras=para_start, map=list(m.items())[:5]), io.open(os.path.join(D,'AI語譯','_work','ys_align_stats.json'),'w',encoding='utf-8'))
