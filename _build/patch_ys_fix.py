import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'

# 1) 修正業疏卷首白話順序
tp = os.path.join(B, 'AI語譯', 'out', '03_業疏', '00_卷首.txt')
tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(tp, encoding='utf-8').read()) if x.strip()]
print('原', len(tt))
fixed = [
    tt[2],                                   # 原夫平等法界
    tt[3],                                   # 旹享保第十六載…
    '編號七二八之乙：《會刻羯磨疏記序》',
    tt[4],                                   # 甞聞毗尼藏…
    '時值享保十五年、歲次庚戌（龍舍）秋季七月十五僧自恣日，通受戒苾芻禪龍於泉州萬代莊佛頂山金輪寺丈室敬書。',
]
io.open(tp, 'w', encoding='utf-8').write('\n\n'.join(fixed) + '\n')
print('修正為', len(fixed), '段')
for i, x in enumerate(fixed):
    print(' ', i, x[:40])

# 2) pairs_simple 使用標點表
p = os.path.join(B, '_src', 'site_ju.py')
s = io.open(p, encoding='utf-8').read()
old = """def pairs_simple(src_dir, tr_tag):
    \"\"\"直接以分卷原文配白話（段數已 1:1）。\"\"\"
    res = []
    cur = None
    entries = []
    for key, sp, tt in load_chunks(src_dir, tr_tag):"""
new = """def pairs_simple(src_dir, tr_tag):
    \"\"\"直接以分卷原文配白話（段數已 1:1），有標點表則優先使用。\"\"\"
    punct = None
    pth = os.path.join(B, 'AI語譯', '_work', 'yeshu_punct.json')
    if os.path.exists(pth):
        punct = json.load(io.open(pth, encoding='utf-8'))
    res = []
    cur = None
    entries = []
    gi = -1
    for key, sp, tt in load_chunks(src_dir, tr_tag):"""
if old in s and 'yeshu_punct.json' not in s:
    s = s.replace(old, new)
    old2 = """        n = min(len(sp), len(tt))
        for i in range(n):
            entries.append((sp[i], tt[i]))
        for i in range(n, len(sp)):
            entries.append((sp[i], ''))"""
    new2 = """        n = min(len(sp), len(tt))
        for i in range(n):
            gi += 1
            o = sp[i]
            if punct and gi < len(punct) and re.search(r'[，。、；：？！]', punct[gi]):
                o = punct[gi]
            entries.append((o, tt[i]))
        for i in range(n, len(sp)):
            gi += 1
            entries.append((sp[i], ''))"""
    s = s.replace(old2, new2)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('pairs_simple uses punct')
