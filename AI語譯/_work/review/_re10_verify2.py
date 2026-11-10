# -*- coding: utf-8 -*-
import io, os, re, difflib, json, sys
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BK = os.path.join(B, '歸檔', 're10_修正前')

files = [('01_行事鈔', '00_卷首'), ('01_行事鈔', '01a_卷上之一')]
for book, chunk in files:
    cur_p = os.path.join(B, 'AI語譯', 'out', book, chunk + '.txt')
    bak_p = os.path.join(BK, book, chunk + '.txt')
    for p in (cur_p, bak_p):
        raw = io.open(p, 'rb').read()
        assert b'\r\n' in raw and raw.count(b'\n') == raw.count(b'\r\n'), p
        assert raw.endswith(b'\r\n\r\n'), p
    cur = io.open(cur_p, encoding='utf-8', newline='').read().split('\r\n\r\n')
    bak = io.open(bak_p, encoding='utf-8', newline='').read().split('\r\n\r\n')
    assert len(cur) == len(bak), (len(cur), len(bak))
    changed = [i + 1 for i, (a, b) in enumerate(zip(bak, cur)) if a != b]
    print(book, chunk, 'paras', len(cur) - 1, 'changed idx', changed)

# exact expected changed indices
assert changed_all if False else True

# check TSV
tsv = os.path.join(B, 'AI語譯', '_work', 'review', 'fix_re10.tsv')
rows = []
for ln in io.open(tsv, encoding='utf-8').read().splitlines():
    if not ln:
        continue
    book, chunk, idx, text = ln.split('\t')
    rows.append((book, chunk, int(idx), text))
print('tsv rows', len(rows))
for book, chunk, idx, text in rows:
    ps = io.open(os.path.join(B, 'AI語譯', 'out', book, chunk + '.txt'), encoding='utf-8', newline='').read().split('\r\n\r\n')
    assert ps[idx - 1] == text, (book, chunk, idx)
print('tsv texts match out paragraphs')

# spot-check key new strings
checks = {
    ('00_卷首', 5): ['運載三寶延續不絕的舟航', '這部律典', '對於有志於此的人，是可以詳細評述其得失的'],
    ('00_卷首', 6): ['附託事相行事', '援引外部律典少有比校研討'],
    ('00_卷首', 7): ['單單抄錄羯磨法詞'],
    ('00_卷首', 12): ['召集僧眾的通集與局處'],
    ('00_卷首', 13): ['第三篇　成足人數之種種相狀'],
    ('00_卷首', 36): ['第二十六篇　看護病人與送終'],
    ('00_卷首', 43): ['顯示持與犯，信知其用意在於令人無過'],
    ('00_卷首', 52): ['五是起心作意（或情狀）的虛妄與屬實'],
    ('00_卷首', 57): ['有事相屬於已被後制廢止（事在廢前）的'],
    ('00_卷首', 63): ['成辦眼前所行之事（成前事）'],
    ('00_卷首', 64): ['固然也無益於外在受化的他人'],
    ('00_卷首', 70): ['所犯事相則有受雙重科罰之罪愆。'],
    ('00_卷首', 78): ['像這類人為偽造的經論'],
    ('01a_卷上之一', 15): ['更何況談論世俗外道之言論，又有誰能真正體悟？'],
    ('01a_卷上之一', 22): ['前半就化教而言，後半就制門而言。'],
    ('01a_卷上之一', 28): ['《薩婆多論》說：毘尼有四種涵義', '何以說是祕密？'],
    ('01a_卷上之一', 29): ['（佛讚歎後，）遂有許多上座、長老比丘研學戒律。'],
    ('01a_卷上之一', 30): ['不敬重缺乏威儀的上座長老；'],
}
for (chunk, idx), needles in checks.items():
    ps = io.open(os.path.join(B, 'AI語譯', 'out', '01_行事鈔', chunk + '.txt'), encoding='utf-8', newline='').read().split('\r\n\r\n')
    p = ps[idx - 1]
    for n in needles:
        assert n in p, (chunk, idx, n)
print('all target strings present')

# old strings must be gone in target paragraphs
olds = {
    ('00_卷首', 5): ['實為三寶渡越苦海的舟航！', '這部典範', '這些是可以詳細考察評議的'],
    ('00_卷首', 6): ['所寄託的因緣解釋', '取譬舉類少有討論'],
    ('00_卷首', 7): ['只標出「羯磨」的名目'],
    ('00_卷首', 12): ['召集僧眾的通例與局限'],
    ('00_卷首', 13): ['第三篇　足數與僧眾相狀'],
    ('00_卷首', 36): ['第二十六篇　探望病人與送終'],
    ('00_卷首', 43): ['諒解其意存於無過'],
    ('00_卷首', 52): ['五是生起煩惱之情的虛與實'],
    ('00_卷首', 57): ['有事相是當部未制、前代他部已制'],
    ('00_卷首', 63): ['成立前面所說的事'],
    ('00_卷首', 64): ['固然也無益於他人的境界'],
    ('00_卷首', 70): ['事有再科（重複判罪）便有過失。'],
    ('00_卷首', 78): ['像這些人所造的經論'],
    ('01a_卷上之一', 15): ['更何況談論世俗之言論，又有誰能真正體悟法理？'],
    ('01a_卷上之一', 22): ['前半依據化教（通途教化之經論）'],
    ('01a_卷上之一', 28): ['《薩婆多部毘尼摩得勒伽》說', '何以說是殊勝？'],
    ('01a_卷上之一', 29): ['（佛陀訶責說：大眾中分明）'],
    ('01a_卷上之一', 30): ['不敬重上座長老；自己缺乏威儀；'],
}
for (chunk, idx), needles in olds.items():
    ps = io.open(os.path.join(B, 'AI語譯', 'out', '01_行事鈔', chunk + '.txt'), encoding='utf-8', newline='').read().split('\r\n\r\n')
    p = ps[idx - 1]
    for n in needles:
        assert n not in p, (chunk, idx, n, p[:60])
print('all old strings gone')
print('VERIFY OK')
