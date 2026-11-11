# -*- coding: utf-8 -*-
"""re10_2 套用：19 條 → 15 段（01_行事鈔）。

流程：
1. 備份到 歸檔/re10_2修正前/01_行事鈔/
2. 逐段套用（每條 A 必須在該段恰好出現 1 次）
3. 驗證：段數不變、只有預期段落變動、B 均在、A 均已消失
4. 寫出 fix_re10_2.tsv 與 _log_re10_2_apply.json
"""
import io, os, json, shutil, sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, 'AI語譯', 'out', '01_行事鈔')
BK = os.path.join(B, '歸檔', 're10_2修正前', '01_行事鈔')
REV = os.path.join(B, 'AI語譯', '_work', 'review')

# (chunk, seg) -> [(段號, A, B), ...]
OPS = {
    ('00_卷首', 5): [
        ('001-0005',
         '所以震嶺所傳的教法，九代之間都有人聽聞；能拔萃出類的，不過是靠智慧與方法罷了。',
         '因此自佛法傳入震嶺（東土）以來，九代之中天下聞名、出類拔萃者，也不過是憑藉世智辯術罷了。'),
        ('001-0005',
         '想要顯揚行儀、匡正攝持像教，垂示常法規範、訓導後學，接續已斷的玄妙綱維、樹立已倒下的偉大標表，對於有志於此的人，是可以詳細評述其得失的。',
         '想要顯揚行儀、匡正攝持像教，垂示常法規範、訓導後學，接續已斷的玄妙綱維、樹立已倒下的偉大標表的人，是必須仔細考評審度才能得見的（言其極為罕見）。'),
    ],
    ('00_卷首', 7): [
        ('001-0007',
         '依文而用，便無法辨別前面的事項',
         '依文而用，便不知作法前應備的諸般緣法（前方便事）'),
    ],
    ('00_卷首', 8): [
        ('001-0008',
         '全都收攬為此宗的一種見解',
         '全都收攬為本宗的一家正見（定見）'),
    ],
    ('00_卷首', 26): [
        ('001-0026',
         '第十六篇　懺除六聚法',
         '第十六篇　懺除六聚罪的方法'),
    ],
    ('00_卷首', 29): [
        ('001-0029',
         '第十九篇　鉢器的制定與開聽',
         '第十九篇　鉢器的禁制與開聽'),
    ],
    ('00_卷首', 33): [
        ('001-0033',
         '第二十三篇　訃告、邀請等儀則的設立',
         '第二十三篇　應供赴請儀則的設立'),
    ],
    ('00_卷首', 53): [
        ('001-0053',
         '所以受學律藏的人，立約求學一定要期望經久長遠，',
         '所以從師受學，必須依止經久博通的明師，'),
        ('001-0053',
         '這樣還有什麼事情會遭到毀謗譏嫌，又怎會淪落於無知的責備呢？',
         '怎會遭受毀謗譏嫌，又怎會淪落於遭人嗤笑責難呢？'),
    ],
    ('00_卷首', 58): [
        ('001-0058',
         '那麼涉獵事情時事相就不周全',
         '那麼臨事行法時事相就不周全'),
    ],
    ('00_卷首', 75): [
        ('001-0075',
         '第十，說明這部鈔的撰作。引用正文，去除濫雜、傳述真實，是斟酌科判的用意。首先說明所引用的正經，其次說明世間偽妄之說，最後說明鈔興起的本意。',
         '第十，說明作鈔者引用正文、去除濫雜、傳述真實、斟酌科判的用意。首先說明所引用的正經，其次說明世間偽妄之說，最後說明作鈔興起的本意。'),
    ],
    ('01a_卷上之一', 15): [
        ('001-0097',
         '仍然茫然不知依託與歸宿',
         '仍然昏昧不達事相而盲目行事'),
        ('001-0097',
         '更何況談論世俗外道之言論，又有誰能真正體悟？',
         '更何況那些高談世俗言論之輩，又有誰能體解戒法呢？'),
    ],
    ('01a_卷上之一', 17): [
        ('001-0099',
         '但現在受戒者所納受的，就其圓成之功德而言，稱為「聖法」。',
         '但現在受戒者所納受的，是就聖者已成之聖道（初果以上所修三學）而言，稱為「聖法」。'),
    ],
    ('01a_卷上之一', 21): [
        ('001-0103',
         '首先說明順從戒律，則三寶得以久住維持，辨析比丘應行之事。',
         '首先說明順從戒律，則三寶得以久住維持，成辦比丘事（成辦比丘之佛事）。'),
    ],
    ('01a_卷上之一', 24): [
        ('001-0106',
         '《阿毘曇毘婆沙論》說：具備「戒足」的人，所謂「戒」，梵語稱為尸羅（śīla）',
         '《阿毘曇毘婆沙論》說：所謂「具戒足」，其中「戒」，梵語稱為尸羅（śīla）'),
    ],
    ('01a_卷上之一', 28): [
        ('001-0110',
         '乃至引導達到梵天安住、聖者安住與無餘涅槃境界',
         '乃至引導達到梵住（四無量心）、聖者安住與無餘涅槃境界'),
        ('001-0110',
         '何以說是祕密？因為諸部契經，不論時間、處所、對象皆可宣說',
         '如諸部契經，不論時間、處所、對象皆可宣說'),
    ],
    ('01a_卷上之一', 33): [
        ('001-0115',
         '如果不齊心集會',
         '如果不能全員到齊集會'),
    ],
}

CHUNKS = ['00_卷首', '01a_卷上之一']


def load(chunk):
    p = os.path.join(OUT, chunk + '.txt')
    s = io.open(p, encoding='utf-8', newline='').read()
    assert '\n' in s
    nl = '\r\n' if '\r\n' in s else '\n'
    assert nl == '\r\n', chunk
    parts = s.split('\r\n\r\n')
    assert parts[-1] == '', chunk
    return p, s, parts


def main():
    dry = '--dry' in sys.argv
    os.makedirs(BK, exist_ok=True)

    data = {}
    for ch in CHUNKS:
        p, s, parts = load(ch)
        data[ch] = [p, s, list(parts)]

    # ---- 1. 驗證 A 唯一 ----
    errs = []
    for (ch, seg), ops in sorted(OPS.items(), key=lambda kv: (CHUNKS.index(kv[0][0]), kv[0][1])):
        parts = data[ch][2]
        txt = parts[seg - 1]
        for tag, a, b in ops:
            n = txt.count(a)
            if n != 1:
                errs.append(f'{ch}#{seg} {tag}: A 出現 {n} 次 -> {a[:30]}')
            if b in txt:
                errs.append(f'{ch}#{seg} {tag}: B 已存在（可能重複套用）')
    if errs:
        print('!! 前置檢查失敗')
        for e in errs:
            print('  ', e)
        return 1

    # ---- 2. 備份 ----
    if not dry:
        for ch in CHUNKS:
            src = os.path.join(OUT, ch + '.txt')
            dst = os.path.join(BK, ch + '.txt')
            shutil.copy2(src, dst)
        print('>> 備份完成:', BK)

    # ---- 3. 套用 ----
    old_parts = {}
    for (ch, seg), ops in OPS.items():
        parts = data[ch][2]
        old_parts[(ch, seg)] = parts[seg - 1]
        txt = parts[seg - 1]
        for tag, a, b in ops:
            txt = txt.replace(a, b, 1)
        parts[seg - 1] = txt

    # ---- 4. 驗證 ----
    for ch in CHUNKS:
        p, s, parts = data[ch]
        new_s = '\r\n\r\n'.join(parts)
        old_n = len(s.split('\r\n\r\n'))
        new_n = len(new_s.split('\r\n\r\n'))
        assert old_n == new_n, (ch, old_n, new_n)
        assert new_s.endswith('\r\n\r\n'), ch
        # 只有預期段落變動
        old_sp = s.split('\r\n\r\n')
        changed = [i + 1 for i in range(len(old_sp)) if old_sp[i] != parts[i]]
        expect = sorted(k[1] for k in OPS if k[0] == ch)
        if changed != expect:
            print(f'!! {ch} 變動段落不符：實際 {changed} / 預期 {expect}')
            return 1
        # B 均在、A 均已消失
        for (c2, seg), ops in OPS.items():
            if c2 != ch:
                continue
            for tag, a, b in ops:
                assert b in parts[seg - 1], (ch, seg, b[:30])
                assert a not in parts[seg - 1], (ch, seg, a[:30])
        print(f'OK {ch}: 段數 {new_n-1}，變動段 {changed}')

        if not dry:
            io.open(p, 'w', encoding='utf-8', newline='').write(new_s)

    if dry:
        buf = []
        for ch in CHUNKS:
            for seg in sorted(k[1] for k in OPS if k[0] == ch):
                buf.append('=' * 90)
                buf.append(f'{ch}#{seg}')
                buf.append('-' * 90)
                buf.append(data[ch][2][seg - 1])
                buf.append('')
        io.open(os.path.join(REV, '_re10_2_preview.txt'), 'w',
                encoding='utf-8', newline='\n').write('\n'.join(buf))

    # ---- 5. 輸出 TSV / log ----
    rows = []
    log = []
    for ch in CHUNKS:
        parts = data[ch][2]
        segs = sorted(k[1] for k in OPS if k[0] == ch)
        for seg in segs:
            rows.append('\t'.join(['01_行事鈔', ch, str(seg), parts[seg - 1]]))
            ops = OPS[(ch, seg)]
            log.append({
                'chunk': ch, 'seg': seg,
                'segs': [o[0] for o in ops],
                'old': old_parts[(ch, seg)],
                'new': parts[seg - 1],
                'ops': [{'a': o[1], 'b': o[2]} for o in ops],
            })
    if not dry:
        io.open(os.path.join(REV, 'fix_re10_2.tsv'), 'w',
                encoding='utf-8', newline='').write('\n'.join(rows) + '\n')
        io.open(os.path.join(REV, '_log_re10_2_apply.json'), 'w',
                encoding='utf-8', newline='').write(
                    json.dumps(log, ensure_ascii=False, indent=1))
        print('>> 寫出 fix_re10_2.tsv（%d 列）與 _log_re10_2_apply.json' % len(rows))
    return 0


if __name__ == '__main__':
    sys.exit(main())
