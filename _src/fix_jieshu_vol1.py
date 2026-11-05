import io, re, os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '02_戒疏', '00_卷首.txt')
T = os.path.join(B, 'AI語譯', 'out', '02_戒疏', '00_卷首.txt')

PLAIN = {1, 2, 3, 7, 10, 14, 19, 23, 24, 47, 48, 61, 62}
XU = {4, 5, 6, 8, 9, 11, 12, 13, 15, 16, 17, 18, 63}
FAN = {20, 21, 22}
MU = set(range(25, 47))
TIAO = set(range(49, 61))

SRC_LEAD = re.compile(r'^【[^】]{1,3}】\s*')
OUT_LEAD = re.compile(r'^(【[^】]{1,6}】)+')


def label_of(i):
    if i in XU:
        return '序'
    if i in FAN:
        return '凡例'
    if i in MU:
        return '目錄'
    if i in TIAO:
        return '條目'
    return None


def relabel_src():
    lines = io.open(S, encoding='utf-8').read().split('\n')
    head, body = lines[:5], [x for x in lines[5:] if x.strip()]
    out = []
    for i, s in enumerate(body, 1):
        t = SRC_LEAD.sub('', s.strip())
        L = label_of(i)
        out.append(('【' + L + '】' + t) if L else t)
    io.open(S, 'w', encoding='utf-8').write('\n'.join(head) + '\n' + '\n'.join(out) + '\n')
    print('src relabelled', len(out))


def relabel_out():
    ps = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(T, encoding='utf-8').read()) if x.strip()]
    out = []
    for i, s in enumerate(ps, 1):
        t = OUT_LEAD.sub('', s).strip()
        L = label_of(i)
        out.append(('【' + L + '文】' + t) if L else t)
    io.open(T, 'w', encoding='utf-8').write('\n\n'.join(out) + '\n')
    print('out relabelled', len(out))


FIX = [
    ('鳩摩羅跋提', '佛陀耶舍（覺明）'),
    ('拯救拔拔三界', '拯救拔濟三界'),
    ('自行掘掘土地戒', '自行挖掘土地戒'),
]


def fix_text(p):
    t = io.open(p, encoding='utf-8').read()
    b = t
    for a, c in FIX:
        t = t.replace(a, c)
    if t != b:
        io.open(p, 'w', encoding='utf-8').write(t)
        print('fixed', os.path.basename(p))


relabel_src()
relabel_out()
for f in os.listdir(os.path.join(B, 'AI語譯', 'out', '02_戒疏')):
    if f.endswith('.txt'):
        fix_text(os.path.join(B, 'AI語譯', 'out', '02_戒疏', f))
