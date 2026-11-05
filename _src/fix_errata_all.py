import os, io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'

FIX = {
    ('TXT_分卷', '02_戒疏'): [
        ('交嶋鼓', '交鳴鼓'), ('傳其未也', '傳其末也'), ('此土木無', '此土本無'),
        ('如古三藏流傅', '如古三藏流傳'), ('多起靜競', '多起諍競'), ('怏修梵行', '快修梵行'),
        ('故去「無厭」', '故云「無厭」'), ('戒本後有□十犍度', '戒本後有二十犍度'),
    ],
    ('TXT_分卷', '01_行事鈔'): [
        ('而不宿死戶', '而不宿死屍'),
        ('見眾僧如法羯磨，而心不同', '見眾僧非法羯磨，而心不同'),
        ('量恐不成', '良恐不成'),
        ('法成已不', '法成以不'),
        ('粥時、槳時', '粥時、漿時'),
        ('事緣要必須訃', '事緣要必須赴'),
        ('官作閨月者', '官作閏月者'),
    ],
}

for (root, book), reps in FIX.items():
    d = os.path.join(B, root, book)
    n = 0
    for f in sorted(os.listdir(d)):
        if not f.endswith('.txt'):
            continue
        p = os.path.join(d, f)
        t = io.open(p, encoding='utf-8').read()
        b = t
        for a, c in reps:
            if a in t:
                t = t.replace(a, c)
                n += 1
        if t != b:
            io.open(p, 'w', encoding='utf-8').write(t)
    print(book, 'replacements', n)

# 譯文同步
OUT_FIX = {
    '01_行事鈔': [('如法羯磨', '非法羯磨'), ('量恐不成', '良恐不成'), ('閨月', '閏月'),
                  ('槳時', '漿時'), ('死戶', '死屍')],
}
for tag, reps in OUT_FIX.items():
    d = os.path.join(B, 'AI語譯', 'out', tag)
    n = 0
    for f in sorted(os.listdir(d)):
        if not f.endswith('.txt'):
            continue
        p = os.path.join(d, f)
        t = io.open(p, encoding='utf-8').read()
        b = t
        for a, c in reps:
            if a in t:
                t = t.replace(a, c)
                n += 1
        if t != b:
            io.open(p, 'w', encoding='utf-8').write(t)
    print(tag, '譯文 replacements', n)
