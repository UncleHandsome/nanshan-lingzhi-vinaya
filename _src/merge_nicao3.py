
# -*- coding: utf-8 -*-
import io, re, os
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BT = chr(96) * 3
def han(s): return ''.join(ch for ch in s if '\u4e00' <= ch <= '\u9fff' or ch == '〇')
ju = io.open(os.path.join(D,'04_四分律比丘尼鈔_句讀.txt'), encoding='utf-8').read()
src = han(io.open(os.path.join(D,'TXT','04_四分律比丘尼鈔.txt'), encoding='utf-8').read())
sup = io.open(os.path.join(D,'TXT_句讀','_缺段','補.txt'), encoding='utf-8').read()
blocks = re.findall(BT + r'(?:text)?\r?\n([\s\S]*?)' + BT, sup)
parts = re.split(r'【缺段(\d)】', blocks[1])
segs = {int(parts[i]): parts[i+1].strip() for i in range(1, len(parts), 2)}

def raw_of(text, hancount):
    c = 0
    for i, ch in enumerate(text):
        if '\u4e00' <= ch <= '\u9fff' or ch == '〇':
            c += 1
            if c == hancount: return i + 1
    return len(text)

def after(text, anchor, payload):
    h = han(text); a = han(anchor); pos = h.rfind(a)
    if pos < 0: return None
    raw = raw_of(text, pos + len(a))
    return text[:raw] + payload + text[raw:]

def before(text, anchor, payload):
    h = han(text); a = han(anchor); pos = h.find(a)
    if pos < 0: return None
    raw = raw_of(text, pos)
    return text[:raw] + payload + text[raw:]

ju = after(ju, src[72358:72372], segs[1]) or ju
ju = after(ju, segs[1], segs[2]) or ju
ju = after(ju, src[46822:46836], segs[3]) or ju
ju = before(ju, src[9720:9736], segs[4]) or ju
juh = han(ju)
print('seg4 anchor present?', han(src[9720:9736]) in juh)
io.open(os.path.join(D,'04_四分律比丘尼鈔_句讀_v2.txt'),'w',encoding='utf-8').write(ju)
print('chars', len(ju))
