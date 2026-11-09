# -*- coding: utf-8 -*-
"""Build fix_r8_g2.tsv for books 02_戒疏 / 資持記 / 01_行事鈔.
Base = live paragraph in AI語譯/out/<book>/<chunk>.txt (which already contains
the auto-applied fixes), apply only the remaining problem-specific edits."""
import csv, io, os, re, sys, difflib
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
OPS[('02_戒疏', '15a_卷三下之三', '143')] = [
    ('依止「四依法」而修持', '依止「四依行」而修持', 1),
]
OPS[('02_戒疏', '17c_卷四上之二', '33')] = [
    ('布施畜生勝過外道仙人', '畜生勝過人道', 1),
]
OPS[('02_戒疏', '17c_卷四上之二', '34')] = [
    ('偷蘭難陀比丘尼沒有看見他，便向人吹噓說提婆達多等才是龍中之龍。',
     '比丘尼因沒看見他，便說「龍中之龍」。', 1),
]
OPS[('02_戒疏', '17c_卷四上之二', '42')] = [
    ('然而關於「燈油」的規定，清楚表明了大食（正食）與小食（不正食）吃了都會結重罪，',
     '然而「燈油」一項所得的則是輕罪；至於大食（正食）與小食（不正食），都包含在飲食的犯相之中，吃了都會結重罪，', 1),
]
OPS[('02_戒疏', '17c_卷四上之二', '53')] = [
    ('以及與比丘尼等出家四眾相約同行', '以及與比丘尼等出家四眾同行', 1),
]
OPS[('02_戒疏', '17c_卷四上之二', '73')] = [
    ('比丘只能暫時借用', '比丘可以使用', 1),
]
OPS[('02_戒疏', '17c_卷四上之二', '74')] = [
    ('接著依據隨機羯磨註來做決斷', '接著依據注文來做決斷', 1),
]
OPS[('02_戒疏', '18b_卷四上之三', '94')] = [
    ('殘宿、內宿，也各有四句。', '殘宿與內宿的對照，也分為四句。', 1),
]
OPS[('02_戒疏', '18b_卷四上之三', '132')] = [
    ('城裡的人為了父母等亡者，在四衢道頭乃至廟中祭祀供養',
     '城裡的人為父母等，在四衢道頭乃至廟中祭祀供養', 1),
]
OPS[('02_戒疏', '19c_卷四下之一', '2')] = [
    ('即使世俗的虛歲未滿', '即使世俗的年歲未滿', 1),
]
OPS[('02_戒疏', '20a_卷四下之二', '81')] = [
    ('既然造成雙方逼近喝斥', '既然造成彼此逼迫斥退', 1),
]
OPS[('02_戒疏', '20a_卷四下之二', '93')] = [
    ('更何況是親眼見到了珍寶與裸露', '更何況是親眼見到了珍寶', 1),
]
OPS[('02_戒疏', '20a_卷四下之二', '94')] = [
    ('散粟王', '粟散王', 1),
]
OPS[('01_行事鈔', '11b_卷下之三', '2')] = [
    ('以及為塔廟營建操勞的優婆塞（在家男居士）', '優婆塞（在家男居士）及經營塔事的人', 1),
]
OPS[('01_行事鈔', '11b_卷下之三', '8')] = [
    ('唯獨不得與女人共同扛抬物品', '唯獨不得與女人同乘一輿', 1),
]
OPS[('資持記', '15b_下三', '60')] = [
    ('將像雕得嗔目怒視、袒胸露臂、揮拳揮臂', '將像雕得嗔目怒視、袒露肩膀、揮拳', 1),
]
OPS[('資持記', '15c_下三', '16')] = [
    ('）接著在明示', '接著在明示', 1),
]
OPS[('資持記', '15c_下三', '17')] = [
    ('所謂「乞請」，就是索求勒索之意。', '所謂「乞請」，就是請求、索求。', 1),
]

ORDER = [
    ('02_戒疏', '15a_卷三下之三', '143'),
    ('02_戒疏', '17c_卷四上之二', '33'),
    ('02_戒疏', '17c_卷四上之二', '34'),
    ('02_戒疏', '17c_卷四上之二', '42'),
    ('02_戒疏', '17c_卷四上之二', '53'),
    ('02_戒疏', '17c_卷四上之二', '73'),
    ('02_戒疏', '17c_卷四上之二', '74'),
    ('02_戒疏', '18b_卷四上之三', '94'),
    ('02_戒疏', '18b_卷四上之三', '132'),
    ('02_戒疏', '19c_卷四下之一', '2'),
    ('02_戒疏', '20a_卷四下之二', '81'),
    ('02_戒疏', '20a_卷四下之二', '93'),
    ('02_戒疏', '20a_卷四下之二', '94'),
    ('01_行事鈔', '11b_卷下之三', '2'),
    ('01_行事鈔', '11b_卷下之三', '8'),
    ('資持記', '15b_下三', '60'),
    ('資持記', '15c_下三', '16'),
    ('資持記', '15c_下三', '17'),
]

assert set(ORDER) == set(OPS), set(ORDER) ^ set(OPS)

rows = []
for key in ORDER:
    book, chunk, seg = key
    base = para(book, chunk, seg)
    new = base
    for old, rep, cnt in OPS[key]:
        n = new.count(old)
        if n != cnt:
            raise SystemExit('COUNT MISMATCH %r in %s/%s#%s: found %d expected %d' % (old, book, chunk, seg, n, cnt))
        new = new.replace(old, rep)
    if new == base:
        raise SystemExit('NO CHANGE %s/%s#%s' % key)
    if '\t' in new or '\n' in new or '\r' in new:
        raise SystemExit('BAD CHAR in %s/%s#%s' % key)
    rows.append((book, chunk, seg, base, new))

with io.open('AI語譯/_work/review/fix_r8_g2.tsv', 'w', encoding='utf-8', newline='') as f:
    for book, chunk, seg, base, new in rows:
        f.write('%s\t%s\t%s\t%s\n' % (book, chunk, seg, new))

print('wrote %d rows' % len(rows))
for book, chunk, seg, base, new in rows:
    print('--- %s %s#%s  %d -> %d' % (book, chunk, seg, len(base), len(new)))
    sm = difflib.SequenceMatcher(None, base, new, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        print('    %-7s %r' % ('base', base[max(0, i1 - 15):i2 + 15]))
        print('    %-7s %r' % ('new', new[max(0, j1 - 15):j2 + 15]))
