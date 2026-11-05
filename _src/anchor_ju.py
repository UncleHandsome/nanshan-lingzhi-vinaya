
# -*- coding: utf-8 -*-
import io, os, re, bisect, json
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
ju_raw=io.open(os.path.join(D,'03_四分律刪補隨機羯磨疏_句讀_clean.txt'),encoding='utf-8').read()
ju=''.join(nh(c) for c in ju_raw if ishan(c))
# 錨點：每 40 字取 20 字片段，唯一者保留
anchors=[]
K=20; STEP=40
for p in range(0, len(src)-K, STEP):
    seg = src[p:p+K]
    if len(set(seg)) < 8: continue
    q = ju.find(seg)
    if q < 0: continue
    if ju.find(seg, q+1) >= 0: continue
    anchors.append((p, q))
print('anchors', len(anchors), 'src', len(src), 'ju', len(ju))
aps=[a for a,_ in anchors]; ajs=[b for _,b in anchors]
# 檢查單調
bad=sum(1 for i in range(1,len(anchors)) if anchors[i][1] < anchors[i-1][1])
print('non-monotonic', bad)
json.dump(anchors, io.open(os.path.join(D,'AI語譯','_work','ys_anchors.json'),'w',encoding='utf-8'))
