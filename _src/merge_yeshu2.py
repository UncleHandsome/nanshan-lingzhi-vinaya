
# -*- coding: utf-8 -*-
import io, os
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
VAR = {'牀':'床','説':'說','衆':'眾','爲':'為','敎':'教','卽':'即','旣':'既','竝':'並'}
def nh(ch): return VAR.get(ch, ch)
def han(s): return ''.join(nh(ch) for ch in s if '\u4e00' <= ch <= '\u9fff' or ch == '〇')
raw_src = io.open(os.path.join(D,'TXT','03_四分律刪補隨機羯磨疏.txt'), encoding='utf-8').read()
src = han(raw_src)
ju_raw = io.open(os.path.join(D,'03_四分律刪補隨機羯磨疏_句讀.txt'), encoding='utf-8').read()
ju = han(ju_raw)
k = 12
jush = set(ju[i:i+k] for i in range(len(ju)-k))
miss = [i for i in range(0, len(src)-k, k) if src[i:i+k] not in jush]
runs = []; cur = None
for i in miss:
    if cur and i <= cur[1]+k: cur[1] = i
    else:
        if cur: runs.append(cur)
        cur = [i, i]
if cur: runs.append(cur)
gaps = sorted([r for r in runs if r[1]-r[0] >= 24], key=lambda r: r[0])
print('gaps', len(gaps))

sup_raw = io.open(os.path.join(D,'TXT_句讀','_缺段','補2.txt'), encoding='utf-8').read()
sup = han(sup_raw)
# 建立 sup 漢字索引 -> raw 位置
sup_idx = [i for i, ch in enumerate(sup_raw) if '\u4e00' <= ch <= '\u9fff' or ch == '〇']
def sup_slice(start, length):
    a = sup_idx[start]; b = sup_idx[min(len(sup_idx)-1, start+length-1)]
    return sup_raw[a:b+1]

# 由後往前插回
out = ju_raw
for a, b, in sorted(gaps, reverse=True):
    glen = (b + k) - a
    needle = src[a:a+40]
    pos = sup.find(needle)
    if pos < 0:
        print('skip gap', a, 'no needle'); continue
    piece = sup_slice(pos, glen)
    # 錨點：後文
    tail = src[b+k:b+k+30]
    # 在 out 中找 tail 的漢字位置
    chars = []; raws = []
    for i, ch in enumerate(out):
        if '\u4e00' <= ch <= '\u9fff' or ch == '〇':
            chars.append(nh(ch)); raws.append(i)
    h = ''.join(chars)
    tpos = h.find(tail)
    if tpos < 0:
        print('skip gap', a, 'no anchor'); continue
    insert_at = raws[tpos]
    out = out[:insert_at] + piece + out[insert_at:]
    print('inserted gap at', a, 'len', glen)
# 清掉開頭對話殘留
i = out.find('四分律刪補隨機羯磨疏')
if i > 0: out = out[i:]
io.open(os.path.join(D,'03_四分律刪補隨機羯磨疏_句讀_v2.txt'),'w',encoding='utf-8').write(out)
print('saved chars', len(out))
