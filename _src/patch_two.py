
# -*- coding: utf-8 -*-
import io, os, re
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
VAR = {'牀':'床','説':'說','衆':'眾','爲':'為','敎':'教','卽':'即','旣':'既','竝':'並'}
def nh(ch): return VAR.get(ch, ch)
def han(s): return ''.join(nh(ch) for ch in s if '\u4e00' <= ch <= '\u9fff' or ch == '〇')
raw_src = io.open(os.path.join(D,'TXT','03_四分律刪補隨機羯磨疏.txt'), encoding='utf-8').read()
src = han(raw_src)
raw_idx = [i for i, ch in enumerate(raw_src) if '\u4e00' <= ch <= '\u9fff' or ch == '〇']
out = io.open(os.path.join(D,'03_四分律刪補隨機羯磨疏_句讀_clean.txt'), encoding='utf-8').read()
def insert_before_tail(out, tail, piece, minpos=0):
    chars=[]; raws=[]
    for i,ch in enumerate(out):
        if '\u4e00' <= ch <= '\u9fff' or ch == '〇':
            chars.append(nh(ch)); raws.append(i)
    h=''.join(chars)
    pos = h.find(tail, minpos)
    if pos < 0: return None
    return out[:raws[pos]] + piece + out[raws[pos]:]
gaps = [(10848,10884),(39444,39480)]
k=12
for a,b in sorted(gaps, reverse=True):
    piece = raw_src[raw_idx[a]:raw_idx[min(len(raw_idx)-1,b+k-1)]+1]
    tail = src[b+k:b+k+20]
    # 先用後文錨點
    r = insert_before_tail(out, tail, piece)
    if r is None:
        # 退而用前文 8 字
        pre = src[max(0,a-8):a]
        chars=[]; raws=[]
        for i,ch in enumerate(out):
            if '\u4e00' <= ch <= '\u9fff' or ch == '〇':
                chars.append(nh(ch)); raws.append(i)
        h=''.join(chars); p=h.find(pre)
        if p >= 0:
            cut = raws[p+len(pre)-1]+1
            out = out[:cut] + piece + out[cut:]
            print('inserted by prefix', a)
        else:
            print('FAILED', a)
    else:
        out = r; print('inserted by tail', a)
io.open(os.path.join(D,'03_四分律刪補隨機羯磨疏_句讀_clean.txt'),'w',encoding='utf-8').write(out)
print('chars', len(out))
