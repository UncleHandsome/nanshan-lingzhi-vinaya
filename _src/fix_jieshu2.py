import os, io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '02_戒疏')
T = os.path.join(B, 'AI語譯', 'out', '02_戒疏')

COMMON = [
    ('僧祗', '僧祇'),
    ('𠎝', '愆'),
    ('𮌎', '胸'),
    ('𠷢', '銜'),
    ('固窮□', '固窮'),
    ('「左右顧視」。（', '「左右顧視」。'),
]

SRC_ONLY = [('壞正之「智」', '懷正之「智」')]

TAIL1_OLD = '言「遮制」者，出經意也。「不同此」者，此有十戒少分法故。'
TAIL1_NEW = ('注文中說「防非遮止」，是點明《善生經》的立意本旨；說「這與此地的情況不同」，'
             '是因為沙彌具有十戒這套屬於出家少分法的戒體緣故。')

TAIL2_OLD = ('《善見論》結「吉」，示不同故。「十」下，次明犯重。「先用盡」者，謂己用過他所貸物。'
             '「後斷當」者，謂主來求索，抵拒不還也。「先斷當」者，謂貸物猶在，故約「離處」方犯。'
             '「受寄亦爾」者，抵拒斷當，犯相並同。次引《善見》，謂負餘人債，比丘輒爾為他持還，'
             '但不成盜，義應有罪。')
TAIL2_NEW = ('《善見論》則判定為「突吉羅」，顯示了部派間的見解差異。「十」字以下，接著說明犯重罪的情況：'
             '「先用盡」是指已經花用耗盡了別人所借貸的物品；「後斷當」是指物主前來索討時，耍賴抗拒不還；'
             '「先斷當」是指借貸之物還在身邊，所以必須以「移離原處」才判定犯罪；「受寄亦爾」是指受託保管的物品'
             '也是如此，只要耍賴拒還，罪相完全相同。接著引用《善見論》，是說他人欠下外債，比丘擅自拿欠債人的'
             '物品替他償還，這雖不構成偷盜罪，但於法義上仍應結罪。')


def apply(base, reps, label):
    tot = {}
    for f in sorted(os.listdir(base)):
        if not f.endswith('.txt'):
            continue
        p = os.path.join(base, f)
        t = io.open(p, encoding='utf-8').read()
        b = t
        for a, c in reps:
            if a in t:
                tot[a] = tot.get(a, 0) + t.count(a)
                t = t.replace(a, c)
        if t != b:
            io.open(p, 'w', encoding='utf-8').write(t)
    print(label, tot)


apply(S, COMMON + SRC_ONLY, 'SRC')
apply(T, COMMON + [(TAIL1_OLD, TAIL1_NEW), (TAIL2_OLD, TAIL2_NEW)], 'OUT')
