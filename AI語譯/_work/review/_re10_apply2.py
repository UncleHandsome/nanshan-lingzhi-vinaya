# -*- coding: utf-8 -*-
"""套用 疑慮_10K/re10.txt 中判定「成立」的修正。

段號（001-0111）先經 校閱_80K/校閱_001.txt 的
「【001-0111】01_行事鈔/01a_卷上之一#29」對到 out 檔與段序。
每段以空行分隔；替換前要求 A 在該段恰好出現一次。
"""
import io, os, re, json, sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
REVIEW = os.path.join(B, 'AI語譯', '_work', 'review')

# (段號, book, chunk, 段序, A, B, 備註)
FIXES = [
    ('001-0005', '01_行事鈔', '00_卷首', 5,
     '實為三寶渡越苦海的舟航！', '實為運載三寶延續不絕的舟航！', ''),
    ('001-0005', '01_行事鈔', '00_卷首', 5,
     '這部典範', '這部律典', ''),
    ('001-0005', '01_行事鈔', '00_卷首', 5,
     '這些是可以詳細考察評議的', '對於有志於此的人，是可以詳細評述其得失的', ''),
    ('001-0006', '01_行事鈔', '00_卷首', 6,
     '所寄託的因緣解釋', '附託事相行事', ''),
    ('001-0006', '01_行事鈔', '00_卷首', 6,
     '取譬舉類少有討論', '援引外部律典少有比校研討', ''),
    ('001-0007', '01_行事鈔', '00_卷首', 7,
     '只標出「羯磨」的名目', '單單抄錄羯磨法詞', '原文以『』包「羯磨」，實際段內作「」'),
    ('001-0012', '01_行事鈔', '00_卷首', 12,
     '召集僧眾的通例與局限', '召集僧眾的通集與局處', ''),
    ('001-0013', '01_行事鈔', '00_卷首', 13,
     '第三篇　足數與僧眾相狀', '第三篇　成足人數之種種相狀', ''),
    ('001-0036', '01_行事鈔', '00_卷首', 36,
     '第二十六篇　探望病人與送終', '第二十六篇　看護病人與送終',
     '改法僅列新句，依段內文定位舊句'),
    ('001-0043', '01_行事鈔', '00_卷首', 43,
     '顯示持與犯，諒解其意存於無過', '顯示持與犯，信知其用意在於令人無過',
     '改法僅列新句，依段內文定位舊句'),
    ('001-0052', '01_行事鈔', '00_卷首', 52,
     '五是生起煩惱之情的虛與實', '五是起心作意（或情狀）的虛妄與屬實', ''),
    ('001-0057', '01_行事鈔', '00_卷首', 57,
     '有事相是當部未制、前代他部已制（事在廢前）的', '有事相屬於已被後制廢止（事在廢前）的', ''),
    ('001-0063', '01_行事鈔', '00_卷首', 63,
     '成立前面所說的事', '成辦眼前所行之事（成前事）', ''),
    ('001-0064', '01_行事鈔', '00_卷首', 64,
     '固然也無益於他人的境界', '固然也無益於外在受化的他人', ''),
    ('001-0070', '01_行事鈔', '00_卷首', 70,
     '事有再科（重複判罪）便有過失。', '所犯事相則有受雙重科罰之罪愆。', ''),
    ('001-0078', '01_行事鈔', '00_卷首', 78,
     '像這些人所造的經論', '像這類人為偽造的經論', '改法僅列新句，依段內文定位舊句'),
    ('001-0097', '01_行事鈔', '01a_卷上之一', 15,
     '更何況談論世俗之言論，又有誰能真正體悟法理？', '更何況談論世俗外道之言論，又有誰能真正體悟？',
     '改法僅列新句，依段內文定位舊句'),
    ('001-0104', '01_行事鈔', '01a_卷上之一', 22,
     '前半依據化教（通途教化之經論），後半依據制門（僧團戒律之制法）。', '前半就化教而言，後半就制門而言。',
     '改法僅列新句，依段內文定位舊句'),
    ('001-0110', '01_行事鈔', '01a_卷上之一', 28,
     '《薩婆多部毘尼摩得勒伽》說', '《薩婆多論》說', ''),
    ('001-0110', '01_行事鈔', '01a_卷上之一', 28,
     '何以說是殊勝？', '何以說是祕密？', ''),
    ('001-0111', '01_行事鈔', '01a_卷上之一', 29,
     '（佛陀訶責說：大眾中分明）有許多上座、長老比丘研學戒律，（你們年輕人為何反而廢學？）',
     '（佛讚歎後，）遂有許多上座、長老比丘研學戒律。', ''),
    ('001-0112', '01_行事鈔', '01a_卷上之一', 30,
     '不敬重上座長老；自己缺乏威儀；', '不敬重缺乏威儀的上座長老；', ''),
]

# 群組：book/chunk -> {idx: [(A,B,note,seg)]}
groups = {}
for seg, book, chunk, idx, a, b, note in FIXES:
    groups.setdefault((book, chunk), {}).setdefault(idx, []).append((seg, a, b, note))

log = []
rows = []
for (book, chunk), segs in groups.items():
    path = os.path.join(B, 'AI語譯', 'out', book, chunk + '.txt')
    raw = io.open(path, encoding='utf-8', newline='').read()
    if '\r\n\r\n' not in raw:
        raise SystemExit('unexpected separator: ' + path)
    parts = raw.split('\r\n\r\n')
    trailing = parts[-1] == ''
    paras = parts[:-1] if trailing else parts[:]
    for idx in sorted(segs):
        p = paras[idx - 1]
        orig = p
        for seg, a, b, note in segs[idx]:
            n = p.count(a)
            if n != 1:
                raise SystemExit('A count=%d (need 1): %s %s#%d %r' % (n, seg, chunk, idx, a))
            p = p.replace(a, b, 1)
            log.append({'seg': seg, 'book': book, 'chunk': chunk, 'idx': idx,
                        'old': a, 'new': b, 'note': note, 'ok': True})
        if p == orig:
            raise SystemExit('no change: %s#%d' % (chunk, idx))
        paras[idx - 1] = p
        rows.append((book, chunk, idx, p))
    out = '\r\n\r\n'.join(paras) + ('\r\n\r\n' if trailing else '')
    io.open(path, 'w', encoding='utf-8', newline='').write(out)
    print('wrote', path)

# TSV：book / chunk / seg / new（沿用既有 fix_*.tsv 無表頭慣例）
tsv = os.path.join(REVIEW, 'fix_re10.tsv')
with io.open(tsv, 'w', encoding='utf-8', newline='') as f:
    for book, chunk, idx, text in rows:
        assert '\t' not in text and '\n' not in text and '\r' not in text
        f.write('%s\t%s\t%d\t%s\n' % (book, chunk, idx, text))
print('rows:', len(rows), 'fixes:', len(log))

with io.open(os.path.join(REVIEW, '_log_re10_apply.json'), 'w', encoding='utf-8') as f:
    json.dump({'fixes': len(log), 'segments': len(rows), 'rows': rows and len(rows),
               'detail': log}, f, ensure_ascii=False, indent=1)
