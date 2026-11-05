
# -*- coding: utf-8 -*-
import io, re, os
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BT = chr(96) * 3
VAR = {'牀':'床','説':'說','衆':'眾','爲':'為','敎':'教','卽':'即','旣':'既','竝':'並'}
def norm(ch): return VAR.get(ch, ch)
def han(s): return ''.join(norm(ch) for ch in s if '\u4e00' <= ch <= '\u9fff' or ch == '〇')

ju = io.open(os.path.join(D,'05_四分律拾毗尼義鈔_句讀.txt'), encoding='utf-8').read()
sup = io.open(os.path.join(D,'TXT_句讀','_缺段','補.txt'), encoding='utf-8').read()
blocks = re.findall(BT + r'(?:text)?\r?\n([\s\S]*?)' + BT, sup)
parts = re.split(r'【缺段(一|二)】', blocks[0])
segs = {}
for i in range(1, len(parts), 2):
    segs[parts[i]] = parts[i+1].strip()
print('patch', {k: len(v) for k, v in segs.items()})

def insert_before(text, anchor, payload):
    chars = []; raw = []
    for i, ch in enumerate(text):
        if '\u4e00' <= ch <= '\u9fff' or ch == '〇':
            chars.append(norm(ch)); raw.append(i)
    h = ''.join(chars); a = han(anchor)
    pos = h.find(a)
    if pos < 0: return None
    idx = raw[pos] if pos < len(raw) else len(text)
    return text[:idx] + payload + text[idx:]

def insert_after(text, anchor, payload):
    chars = []; raw = []
    for i, ch in enumerate(text):
        if '\u4e00' <= ch <= '\u9fff' or ch == '〇':
            chars.append(norm(ch)); raw.append(i)
    h = ''.join(chars); a = han(anchor)
    pos = h.rfind(a)
    if pos < 0: return None
    end = pos + len(a)
    idx = raw[end-1] + 1 if end-1 < len(raw) else len(text)
    return text[:idx] + payload + text[idx:]

# 缺段一：原缺 10128-16608，前文 「說四依」後
j1 = insert_after(ju, '說四依', segs['一'])
print('seg1', bool(j1)); ju = j1 or ju
# 缺段二：原缺 8904-8964
j2 = insert_after(ju, '隨中無作一等異亦四種', segs['二'])
print('seg2', bool(j2)); ju = j2 or ju
io.open(os.path.join(D,'05_四分律拾毗尼義鈔_句讀_v2.txt'),'w',encoding='utf-8').write(ju)
print('chars', len(ju))
