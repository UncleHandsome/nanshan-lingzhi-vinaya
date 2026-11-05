
# -*- coding: utf-8 -*-
import io, re, os
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BT = chr(96) * 3
VAR = {'牀':'床','説':'說','衆':'眾','爲':'為','敎':'教','卽':'即','旣':'既','竝':'並'}
def norm(ch): return VAR.get(ch, ch)
ju = io.open(os.path.join(D,'04_四分律比丘尼鈔_句讀_v2.txt'), encoding='utf-8').read()
sup = io.open(os.path.join(D,'TXT_句讀','_缺段','補.txt'), encoding='utf-8').read()
blocks = re.findall(BT + r'(?:text)?\r?\n([\s\S]*?)' + BT, sup)
parts = re.split(r'【缺段(\d)】', blocks[1])
segs = {int(parts[i]): parts[i+1].strip() for i in range(1, len(parts), 2)}

# 建立 norm 字串與 raw 對應
chars = []; rawpos = []
for i, ch in enumerate(ju):
    if '\u4e00' <= ch <= '\u9fff' or ch == '〇':
        chars.append(norm(ch)); rawpos.append(i)
h = ''.join(chars)
anchor = '是沙彌尼戒能持'
pos = h.rfind(anchor)
print('anchor at', pos)
if pos >= 0:
    end = pos + len(anchor)
    raw = rawpos[end - 1] + 1
    ju = ju[:raw] + segs[4] + ju[raw:]
    io.open(os.path.join(D,'04_四分律比丘尼鈔_句讀_v2.txt'),'w',encoding='utf-8').write(ju)
    print('inserted seg4, chars', len(ju))
