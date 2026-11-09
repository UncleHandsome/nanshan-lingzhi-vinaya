# -*- coding: utf-8 -*-
"""Build fix_r8b_g2.tsv (books 資持記 / 02_戒疏 / 01_行事鈔).
Base = live paragraph in AI語譯/out/<book>/<chunk>.txt.
Only rows whose problem is still present in the live paragraph get an entry.
"""
import io, os, re, sys, difflib
sys.stdout.reconfigure(encoding='utf-8')

CACHE = {}
def paras(book, chunk):
    k = (book, chunk)
    if k not in CACHE:
        p = os.path.join('AI語譯', 'out', book, chunk + '.txt')
        CACHE[k] = [x for x in re.split(r'\r?\n\r?\n', io.open(p, encoding='utf-8').read()) if x.strip()]
    return CACHE[k]

def para(book, chunk, seg):
    return paras(book, chunk)[int(seg) - 1]

# (book, chunk, seg) -> list of (old, new, expected_count)
OPS = {}
OPS[('資持記', '15e_下三', '57')] = [
    ('規定互相跪拜用互跪（胡跪，右膝著地）', '規定用互跪（胡跪，右膝著地）', 1),
]
OPS[('01_行事鈔', '12a_卷下之四', '6')] = [
    ('《摩得伽》說：宿觸等不清淨的動物油脂與肉類，', '《摩得伽》說：不清淨的膏肉，', 1),
]
OPS[('資持記', '16a_下四', '13')] = [
    ('「非道」則是指世俗人間的情執', '「非道」則是指世間法', 1),
]
OPS[('01_行事鈔', '12a_卷下之四', '12')] = [
    ('如果那病人故意手持粗劣的衣缽示人', '如果那病人故意受持粗劣的衣缽', 1),
    ('而把好的衣缽轉送寄託給他人', '而把好的衣缽轉送給他人', 1),
]
OPS[('資持記', '16a_下四', '33')] = [
    ('首先引述《大般涅槃經》作為例證', '首先引佛陀涅槃（雙林入滅）之事為例', 1),
]
OPS[('01_行事鈔', '12a_卷下之四', '16')] = [
    ('世尊及出家五眾皆得為其起塔', '為世尊（如來）起塔，出家五眾皆得興建', 1),
]
OPS[('資持記', '16a_下四', '34')] = [
    ('完全聽憑長者的尊意', '完全聽憑對方（受弔者）的意思', 1),
]
OPS[('資持記', '16a_下四', '36')] = [
    ('所謂「責令賠償」', '所謂「責令加倍償還」', 1),
    ('從「那」字以下', '從「其」字以下', 1),
]
OPS[('資持記', '16a_下四', '38')] = [
    ('該經的後段又記載', '又《涅槃經後分》記載', 1),
]
OPS[('資持記', '16a_下四', '40')] = [
    ('從「依照」以下', '從「準」字以下', 1),
]
OPS[('資持記', '16a_下四', '43')] = [
    ('從「因此」以下', '從「故」字以下', 1),
]
OPS[('資持記', '16a_下四', '50')] = [
    ('若給予忌諱之物導致病情惡化而結罪', '若給予忌諱之物而結罪', 1),
]
OPS[('資持記', '16a_下四', '52')] = [
    ('注文中，首句說明在上座說法開示時應靜聽，次句開示在上座開演時不得夾雜世俗雜語。',
     '注文中，首句闡明上文的「說法」，次句顯示上文的「不雜語」。', 1),
    ('第五、必要時示意大眾保持靜默', '第五、令自身保持沉默', 1),
    ('《善見律》闡明下座比丘向前輩辭謝時的威儀', '《善見律》闡明下法座、禮僧辭謝的威儀', 1),
    ('是指使用象牙等珍貴材質來裝飾拂塵等器具', '是指用象牙來裝飾（法扇）', 1),
]
OPS[('資持記', '16a_下四', '53')] = [
    (None, '《大智度論》說：佛陀是人中的獅子，佛陀所坐的地方，無論是床或是地面，都稱為「師子座」。《僧祇律》說明莊嚴法座的作法；所謂「拂華坐」，是為了去除奢華華美的緣故。第三科中，首先說明進入殿堂時的威儀。所謂「傍門面」，是指隨著左右門頰的方向舉足而入。從「右」字以下，其次指示打椎的方法。所謂「擬砧」，是使椎與砧互相對準；所謂「重響」，是指震動所發的餘聲。下椎的次數不容易辨明，所以必須用左手按住它。〔舊說認為這是表示僧眾心意不一，這是錯誤的；又曾見打椎的人，以左手就著椎作旋轉之勢，更是可笑。〕從「然」字以下，第三說明啟白之事。', 0),
]
OPS[('資持記', '16a_下四', '60')] = [
    ('所謂「破壞出家相貌」', '所謂「破犯戒相」', 1),
]
OPS[('資持記', '16a_下四', '62')] = [
    ('是指倚仗世俗權勢私自霸占信徒檀越', '是指私自霸占信徒檀越', 1),
]
OPS[('資持記', '16a_下四', '57')] = [
    ('是通指三藏十二部教法中所詮釋的真實義理', '是通指三藏的教法詮言', 1),
]
OPS[('01_行事鈔', '12a_卷下之四', '38')] = [
    ('對他人稱讚美譽的慳吝', '吝於稱歎他人之善', 1),
]

ORDER = [
    ('資持記', '15e_下三', '57'),
    ('01_行事鈔', '12a_卷下之四', '6'),
    ('資持記', '16a_下四', '13'),
    ('01_行事鈔', '12a_卷下之四', '12'),
    ('資持記', '16a_下四', '33'),
    ('01_行事鈔', '12a_卷下之四', '16'),
    ('資持記', '16a_下四', '34'),
    ('資持記', '16a_下四', '36'),
    ('資持記', '16a_下四', '38'),
    ('資持記', '16a_下四', '40'),
    ('資持記', '16a_下四', '43'),
    ('資持記', '16a_下四', '50'),
    ('資持記', '16a_下四', '52'),
    ('資持記', '16a_下四', '53'),
    ('資持記', '16a_下四', '60'),
    ('資持記', '16a_下四', '62'),
    ('資持記', '16a_下四', '57'),
    ('01_行事鈔', '12a_卷下之四', '38'),
]
assert set(ORDER) == set(OPS), set(ORDER) ^ set(OPS)

rows = []
problems = []
for key in ORDER:
    book, chunk, seg = key
    base = para(book, chunk, seg)
    new = base
    for old, rep, cnt in OPS[key]:
        if old is None:
            new = rep
            continue
        n = new.count(old)
        if n != cnt:
            problems.append('COUNT %r in %s/%s#%s found %d expected %d' % (old, book, chunk, seg, n, cnt))
            continue
        new = new.replace(old, rep)
    if new == base:
        problems.append('NO CHANGE %s/%s#%s' % (book, chunk, seg))
        continue
    if '\t' in new or '\n' in new or '\r' in new:
        problems.append('BAD CHAR %s/%s#%s' % (book, chunk, seg))
        continue
    rows.append((book, chunk, seg, base, new))

if problems:
    print('PROBLEMS:')
    for p in problems:
        print('  ', p)

with io.open(r'AI語譯/_work/review/fix_r8b_g2.tsv', 'w', encoding='utf-8', newline='') as f:
    for book, chunk, seg, base, new in rows:
        f.write('%s\t%s\t%s\t%s\n' % (book, chunk, seg, new))

print('wrote %d rows' % len(rows))
for book, chunk, seg, base, new in rows:
    print('--- %s %s#%s  %d -> %d' % (book, chunk, seg, len(base), len(new)))
    sm = difflib.SequenceMatcher(None, base, new, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        print('    base: %s' % base[max(0, i1 - 12):i2 + 12])
        print('    new : %s' % new[max(0, j1 - 12):j2 + 12])
