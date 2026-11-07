import glob
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\白話'

def set_text(p, text):
    if p.runs:
        for r in p.runs[1:]:
            r.text = ''
        p.runs[0].text = text
    else:
        p.add_run(text)

def find(ps, key, start=0):
    for i in range(start, len(ps)):
        if ps[i].text.strip().startswith(key):
            return i
    return None

def doc(p):
    return Document(glob.glob(B + r'\會本_篇%02d_*.docx' % p)[0])

# ---- 篇19 記040 前後半補譯 ----
f19 = glob.glob(B + r'\會本_篇19_*.docx')[0]
d = doc(19); ps = d.paragraphs
i = find(ps, '【記040】（前半）')
if i is not None:
    set_text(ps[i + 1], '從「比丘」以下，是開許指派道場大眾服役勞作。「比丘」的上字「比」讀作上聲（讀如鄙）。第三節中，引用《僧祇律》。')
j = find(ps, '【記040】（後半）')
if j is not None:
    set_text(ps[j + 1], '第三節中，引用《僧祇律》。開許在牆壁上繪畫。但若是男女交合的圖樣，就屬於淫相，絕不可繪製。《四分律》中，首先說明不可過度華麗裝飾。也不得使用，同前面一樣除去男女交合像之外，其餘也不准繪製。從「阿難」以下，說明接受專屬僧房。從「若」字以下，說明在僧團公有土地上建造房屋。由於土地屬於常住僧團，理應當禮讓客僧；如果佔據不肯讓出，便強制奪回土地歸還僧團。從「若營」以下，說明建築必須堅固。所謂「十二年」，是因為十二年為一整紀的極限之故。從「若營事」以下，說明獎賞負責營造的人員。')
d.save(f19)
print('篇19 記040 ok')

# ---- 篇21 記062 補漏譯 ----
f21 = glob.glob(B + r'\會本_篇21_*.docx')[0]
d = doc(21); ps = d.paragraphs
i = find(ps, '【記062】')
if i is not None:
    b = ps[i + 1]
    if '不能堅持' not in b.text:
        set_text(b, b.text.rstrip() + '若不能堅持則須作法捨戒；未經作法求受則不成行體；未捨而違犯者即屬犯戒。')
d.save(f21)
print('篇21 記062 ok')

# ---- 篇23 記058 補末句 ----
f23 = glob.glob(B + r'\會本_篇23_*.docx')[0]
d = doc(23); ps = d.paragraphs
i = find(ps, '【記058】')
if i is not None:
    b = ps[i + 1]
    if '申時' not in b.text:
        set_text(b, b.text.rstrip() + '下一科引用經典說明佛陀在世時的說法儀軌，令後世弟子依循仿效。「晡」就是申時（下午三點至五點）。')
d.save(f23)
print('篇23 記058 ok')

# ---- 篇27 記048 補末三句 ----
f27 = glob.glob(B + r'\會本_篇27_*.docx')[0]
d = doc(27); ps = d.paragraphs
i = find(ps, '【記048】')
if i is not None:
    b = ps[i + 1]
    if '健者病者' not in b.text:
        set_text(b, b.text.rstrip() + '《十誦律》說：不淨，指宿觸等物，只開許病者使用。《四分律》說：外用者，健者病者都可使用。')
d.save(f27)
print('篇27 記048 ok')

# ---- 篇13 記135 去除篇14 開頭 ----
f13 = glob.glob(B + r'\會本_篇13_*.docx')[0]
d = doc(13); ps = d.paragraphs
i = find(ps, '【記135】')
if i is not None:
    b = ps[i + 1]; t = b.text
    k = t.find('第十四篇')
    if k > 0:
        set_text(b, t[:k].rstrip())
d.save(f13)
print('篇13 記135 ok')

# ---- 篇12 記001 開頭修正 ----
f12 = glob.glob(B + r'\會本_篇12_*.docx')[0]
d = doc(12); ps = d.paragraphs
i = find(ps, '【記001】')
if i is not None:
    b = ps[i + 1]; t = b.text.strip()
    if t.startswith('的名稱'):
        t = '〔自恣篇〕釋' + t
    set_text(b, t)
d.save(f12)
print('篇12 記001 ok')

# ---- 篇22 記080 譯文回前半 ----
f22 = glob.glob(B + r'\會本_篇22_*.docx')[0]
d = doc(22); ps = d.paragraphs
i = find(ps, '【記080】（前半）'); j = find(ps, '【記080】（後半）')
if i is not None and j is not None:
    tail = '拆毀破壞寺院所招感的惡報極其深重，這正好反過來證明了興建寺院的功德無比深廣。'
    b1, b2 = ps[i + 1], ps[j + 1]
    if tail not in b1.text:
        set_text(b1, b1.text.rstrip() + tail)
    if tail in b2.text:
        set_text(b2, b2.text.replace(tail, '', 1).lstrip())
d.save(f22)
print('篇22 記080 ok')

# ---- 篇26 記005 譯文回前半 ----
f26 = glob.glob(B + r'\會本_篇26_*.docx')[0]
d = doc(26); ps = d.paragraphs
i = find(ps, '【記005】（前半）'); j = find(ps, '【記005】（後半）')
if i is not None and j is not None:
    move = ('這是因為世俗之人忌諱僧眾遠送棺木，為了不讓俗人看見招致譏嫌的緣故。從「其餘」以下，最後說明位階在下的沙彌等眾，'
            '律文中略過沒有詳載，所以應當比照辦理。在第三段中，首句指陳前面聖者所立的戒制，次句勸勉大眾切實遵循，'
            '後兩句則指引詳備的文獻，指的便是《僧祇律》的經文。')
    b1, b2 = ps[i + 1], ps[j + 1]
    if move not in b1.text:
        set_text(b1, b1.text.rstrip() + move)
    if move in b2.text:
        set_text(b2, b2.text.replace(move, '', 1).lstrip())
    elif b2.text.startswith(move[:10]):
        set_text(b2, b2.text.replace(move, '', 1).lstrip())
d.save(f26)
print('篇26 記005 ok')
