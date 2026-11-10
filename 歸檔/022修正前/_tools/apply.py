# -*- coding: utf-8 -*-
"""套用 Gemini 真案 19 條修正到 AI語譯/out/01_行事鈔/07b、07c。

只做局部字串替換；每條斷言在該段中恰好出現一次，段數不變。
"""
import os, io, re, json, shutil, hashlib, sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, 'AI語譯', 'out', '01_行事鈔')
BK = os.path.join(B, '歸檔', '022修正前')

segs = json.load(io.open(os.path.join(B, '_tmp022', 'segs.json'), encoding='utf-8'))
segmap = {(s['chunk'], s['seg']): s for s in segs}

# (chunk, seg, old, new, label)
FIX = [
    ('07b_卷中之三', 29, '五、再次進食該食物便結犯', '五、再次進食便結犯', '022-0002(1)'),
    ('07b_卷中之三', 29, '其具體有五種成犯之緣', '構成足食具體有五種條件（五緣）', '022-0002(2)'),
    ('07b_卷中之三', 31, '第一、對方親手接過該食物並認定將其作為食用', '第一、對方接過食物並吃少許（以成殘食）', '022-0004'),
    ('07b_卷中之三', 32, '受持開許不須作餘食法的食物', '受持不作餘食法之頭陀行者（上行不犯）', '022-0005'),
    ('07b_卷中之三', 34,
     '若是如此，為什麼律中只說世俗假立的時間呢？回答說：真實的時間本質，在毘尼律藏中並不予以多說。'
     '因為在家人與外道不得聽聞律藏，若聽聞了實時之說反而容易生起執常邪見；'
     '因此隨順世俗宣說假名的時辰，以便普遍通行於多數凡俗之人。',
     '若是如此，為什麼經中只說假名的時間呢？回答說：真實的時間只在毘尼（律藏）中說。'
     '因為在家人與外道不得聽聞律藏，若在經中聽聞實時反而容易生起執常邪見；'
     '經中宣說假名的時辰，是因為經教通於道俗大眾（通多分）之故。', '022-0007'),
    ('07b_卷中之三', 35,
     '第一、是殘食而非宿食（如上午吃剩的飯未經作法，在中午前自己再吃），結突吉羅（吉羅）。',
     '第一、是殘食而非宿食（如早晨接受三藥（非時、七日、盡形）而未加口法受持，過午失法），結突吉羅（吉羅）。',
     '022-0008(1)'),
    ('07b_卷中之三', 35,
     '第二、是宿食而非殘食（如昨天接受了未曾動口吃過的乾糧，隔天未經重新受授而吃），亦結突吉羅（吉）。',
     '第二、是宿食而非殘食（指食物尚未經受授，但與比丘同室共宿過夜，結內宿突吉羅；若不共宿則無犯），亦結突吉羅（吉）。',
     '022-0008(2)'),
    ('07c_卷中之三', 6, '能夠使受食成立的人，是具足戒比丘', '能受食的人，是具足戒比丘', '022-0016'),
    ('07c_卷中之三', 7, '無論受過教化還是未受教化', '無論是受比丘指使遞送還是自發授與', '022-0017(1)'),
    ('07c_卷中之三', 7, '一天繫綁一次', '按一天的食量各繫結成一分', '022-0017(2)'),
    ('07c_卷中之三', 8, '除了畜生抖落身體的灰塵（非食物不須受）之外', '除了畜生抖落身體的灰塵之外', '022-0018(1)'),
    ('07c_卷中之三', 8, '僧人與尼姑之間可以互相作淨法、互相受食', '僧人與尼姑之間（殘宿惡觸）互望為淨、可以互相受食', '022-0018(2)'),
    ('07c_卷中之三', 9,
     '所求得的食物必須在同一處所受取，若施受雙方一人在陸地、一人在水中或空中，則受食不能成立。',
     '所求得的食物必須在同一處所受取，處所限於陸地及水中；若在空中受食，則不能成立。', '022-0019(1)'),
    ('07c_卷中之三', 9, '這如同前面關於受食處所的說明。', '這如同前面能受人門中的說明。', '022-0019(2)'),
    ('07c_卷中之三', 10, '請稍微提起來遞給我', '請分批少量遞給我', '022-0020(1)'),
    ('07c_卷中之三', 10, '水流雖然連續不斷', '油流雖然連續不斷', '022-0020(2)'),
    ('07c_卷中之三', 13, '都不需要再依翻穢法處理（不必再翻判定為穢物）', '都不需要再依翻穢法清洗令淨', '022-0023'),
    ('07c_卷中之三', 15, '犯重罪（波逸提）', '犯重罪', '022-0025(2)'),
    ('07c_卷中之三', 16,
     '《五分律》說：比丘乞食時，若遇乞丐、流浪兒乞求，或遇犬等牲畜，可以衡量自己的食量，分減一部分布施給他們。',
     '《五分律》說：以乞得的食物施與小兒、施與犬等牲畜時，應衡量自己的食量，分減一部分布施給牠們。', '022-0026'),
]

assert len(FIX) == 19, len(FIX)

os.makedirs(os.path.join(BK, 'AI語譯', 'out', '01_行事鈔'), exist_ok=True)
changed = {}
for chunk in ('07b_卷中之三', '07c_卷中之三'):
    p = os.path.join(OUT, chunk + '.txt')
    raw = io.open(p, encoding='utf-8', newline='').read()
    old_raw = raw
    # 該 chunk 內所有受影響的段
    items = [f for f in FIX if f[0] == chunk]
    # 逐段處理（先取原段文字，再一次替換，避免前後替換互相干擾）
    per_seg = {}
    for _, seg, old, new, label in items:
        per_seg.setdefault(seg, []).append((old, new, label))
    for seg, fixes in per_seg.items():
        s = segmap[(chunk, seg)]
        assert s['trans'] in raw, (chunk, seg)
        newpara = s['trans']
        for old, new, label in fixes:
            n = newpara.count(old)
            assert n == 1, '%s: count=%d for %r' % (label, n, old[:40])
            newpara = newpara.replace(old, new)
        assert raw.count(s['trans']) == 1, (chunk, seg, 'para not unique')
        raw = raw.replace(s['trans'], newpara, 1)
    # 段數不變
    before = [x for x in re.split(r'\r?\n\r?\n', old_raw) if x.strip()]
    after = [x for x in re.split(r'\r?\n\r?\n', raw) if x.strip()]
    assert len(before) == len(after), (chunk, len(before), len(after))
    changed[chunk] = (old_raw, raw, len(before))
    print('%-14s 段數 %d → %d，修正 %d 條' % (chunk, len(before), len(after), len(items)))

# 備份（先寫檔，內容為修改前）
for chunk, (old_raw, raw, _) in changed.items():
    p = os.path.join(BK, 'AI語譯', 'out', '01_行事鈔', chunk + '.txt')
    io.open(p, 'w', encoding='utf-8', newline='').write(old_raw)
    print('備份', p)

# 寫回
for chunk, (old_raw, raw, _) in changed.items():
    p = os.path.join(OUT, chunk + '.txt')
    io.open(p, 'w', encoding='utf-8', newline='').write(raw)
    print('寫回', p)

# 逐條 diff 摘要
for _, seg, old, new, label in FIX:
    print('\n[%s] %s#%d' % (label, seg, seg))
    print('  - ' + old)
    print('  + ' + new)
