import io, os, re, bisect

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
VAR = {'牀': '床', '説': '說', '衆': '眾', '爲': '為', '敎': '教', '卽': '即', '旣': '既', '竝': '並',
       '収': '收', '煑': '煮', '査': '查', '污': '汙', '於': '于'}


def ishan(c):
    return '\u4e00' <= c <= '\u9fff' or c == '〇'


def hs(s):
    return ''.join(VAR.get(c, c) for c in s if ishan(c))


key = '17b_卷三之六'
sp = [x.strip() for x in io.open(os.path.join(B, 'TXT_分卷', '03_業疏', key + '.txt'), encoding='utf-8').read().split('\n')[5:] if x.strip()]
lines = [x.strip() for x in io.open(os.path.join(B, 'TXT_句讀', '03_業疏', key + '.txt'), encoding='utf-8').read().split('\n')]
noise = re.compile(r'^(=+|（句讀版）|四分律.*卷|\.txt)')
jt = ''.join(x for x in lines if x and not noise.match(x) and len(hs(x)) >= 2)
Sp, J = hs(''.join(sp)), hs(jt)
print('sp 字', len(Sp), 'ju 字', len(J))
K, STEP = 16, 8
anchors = []
for p in range(0, max(0, len(Sp) - K), STEP):
    seg = Sp[p:p + K]
    if len(set(seg)) < 8:
        continue
    q = J.find(seg)
    if q < 0 or J.find(seg, q + 1) >= 0:
        continue
    anchors.append((p, q))
print('錨點', len(anchors), anchors[:3], anchors[-3:] if anchors else '')
print('sp 首', Sp[:30])
print('ju 首', J[:30])
