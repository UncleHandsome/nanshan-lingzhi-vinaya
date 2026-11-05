
# -*- coding: utf-8 -*-
import io
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
pairs = [('TXT/04_四分律比丘尼鈔.txt','04_四分律比丘尼鈔_句讀.txt','尼鈔'),
         ('TXT/05_四分律拾毗尼義鈔.txt','05_四分律拾毗尼義鈔_句讀.txt','義鈔')]
def han(s):
    return ''.join(ch for ch in s if '\u4e00' <= ch <= '\u9fff' or ch == '〇')
out = []
for srcp, jup, name in pairs:
    src = han(io.open(B+'/'+srcp, encoding='utf-8').read())
    ju  = han(io.open(B+'/'+jup, encoding='utf-8').read())
    k = 12
    jush = set(ju[i:i+k] for i in range(len(ju)-k))
    miss = [i for i in range(0, len(src)-k, k) if src[i:i+k] not in jush]
    runs = []; cur = None
    for i in miss:
        if cur and i <= cur[1] + k: cur[1] = i
        else:
            if cur: runs.append(cur)
            cur = [i, i]
    if cur: runs.append(cur)
    big = [r for r in runs if r[1]-r[0] >= 24]
    out.append('%s：缺漏區塊 ≥24字 共 %d 段，合計約 %d 字' % (name, len(big), sum(r[1]-r[0]+k for r in big)))
    for a, b in sorted(big, key=lambda r: r[1]-r[0], reverse=True)[:8]:
        out.append('   src[%d:%d]（%d字）起：%s' % (a, b+k, b-a+k, src[a:a+30]))
io.open(B+'/AI語譯/_work/ju_verify.txt','w',encoding='utf-8').write('\n'.join(out))
print('\n'.join(out)[:1200])
