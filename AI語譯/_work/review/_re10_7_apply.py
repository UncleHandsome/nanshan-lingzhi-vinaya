# -*- coding: utf-8 -*-
"""re10_7 套用：7 條 → 6 段（01_行事鈔），其中 0041 的「一、為大慈愍物」判待裁決不套用。

流程：
1. 備份到 歸檔/re10_7修正前/01_行事鈔/
2. 逐段套用（每條 A 必須在該段恰好出現 1 次）
3. 驗證：段數不變、只有預期段落變動、B 均在、A 均已消失
4. 寫出 fix_re10_7.tsv 與 _log_re10_7_apply.json
"""
import io, os, json, shutil, sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
OUT = os.path.join(B, 'AI語譯', 'out', '01_行事鈔')
BK = os.path.join(B, '歸檔', 're10_7修正前', '01_行事鈔')
REV = os.path.join(B, 'AI語譯', '_work', 'review')

# (chunk, seg) -> [(段號, A, B), ...]
OPS = {
    ('00_卷首', 5): [
        ('001-0005',
         '佛法能久住世間，眾多典籍也就到此止息其說',
         '若論及住持佛法，其餘眾多經籍在此皆當止息其唱說（唯律藏獨具此功）'),
    ],
    ('00_卷首', 6): [
        ('001-0006',
         '這樣一來，經文固然可信為實錄',
         '這樣一來，律文固然可信為實錄'),
    ],
    ('00_卷首', 41): [
        ('001-0041',
         '統御教法則一律通用而沒有準則',
         '秉御羯磨法則一律通用而沒有準則'),
    ],
    ('00_卷首', 52): [
        ('001-0052',
         '一是興起厭離心的漸與頓。',
         '一是興（起心）與厭（厭而不學）的漸與頓。'),
    ],
    ('01a_卷上之一', 16): [
        ('001-0098',
         '「戒法雖然沒有形體色相，卻可以持守護持」',
         '「（戒體）雖然沒有形體色相，卻可以持守護持」'),
    ],
    ('01a_卷上之一', 19): [
        ('001-0101',
         '「戒體雖然不是有形質可以觸對之物，但只要善加修習持戒方便，身口就能得到清淨」',
         '「（戒體）雖然不是有形質可以觸對之物，但只要善加修習持戒方便，就能得到清淨」'),
    ],
}

CHUNKS = ['00_卷首', '01a_卷上之一']


def load(chunk):
    p = os.path.join(OUT, chunk + '.txt')
    s = io.open(p, encoding='utf-8', newline='').read()
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
    for (ch, seg), ops in OPS.items():
        txt = data[ch][2][seg - 1]
        for tag, a, b in ops:
            n = txt.count(a)
            if n != 1:
                errs.append('%s#%d %s: A 出現 %d 次 -> %s' % (ch, seg, tag, n, a[:40]))
            if b in txt:
                errs.append('%s#%d %s: B 已存在（可能重複套用）' % (ch, seg, tag))
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
        old_sp = s.split('\r\n\r\n')
        changed = [i + 1 for i in range(len(old_sp)) if old_sp[i] != parts[i]]
        expect = sorted(k[1] for k in OPS if k[0] == ch)
        if changed != expect:
            print('!! %s 變動段落不符：實際 %s / 預期 %s' % (ch, changed, expect))
            return 1
        assert new_s.endswith('\r\n\r\n'), ch
        assert len(old_sp) == len(new_s.split('\r\n\r\n')), ch
        for (c2, seg), ops in OPS.items():
            if c2 != ch:
                continue
            for tag, a, b in ops:
                assert b in parts[seg - 1], (ch, seg, b[:30])
                assert a not in parts[seg - 1], (ch, seg, a[:30])
        print('OK %s: 段數 %d，變動段 %s' % (ch, len(old_sp) - 1, changed))

        if not dry:
            io.open(p, 'w', encoding='utf-8', newline='').write(new_s)

    if dry:
        buf = []
        for ch in CHUNKS:
            for seg in sorted(k[1] for k in OPS if k[0] == ch):
                buf.append('=' * 90)
                buf.append('%s#%d' % (ch, seg))
                buf.append('-' * 90)
                buf.append(data[ch][2][seg - 1])
                buf.append('')
        io.open(os.path.join(REV, '_re10_7_preview.txt'), 'w',
                encoding='utf-8', newline='\n').write('\n'.join(buf))
        print('>> 預覽寫出 _re10_7_preview.txt')

    # ---- 5. 輸出 TSV / log ----
    rows = []
    log = []
    for ch in CHUNKS:
        parts = data[ch][2]
        for seg in sorted(k[1] for k in OPS if k[0] == ch):
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
        io.open(os.path.join(REV, 'fix_re10_7.tsv'), 'w',
                encoding='utf-8', newline='').write('\n'.join(rows) + '\n')
        io.open(os.path.join(REV, '_log_re10_7_apply.json'), 'w',
                encoding='utf-8', newline='').write(
                    json.dumps(log, ensure_ascii=False, indent=1))
        print('>> 寫出 fix_re10_7.tsv（%d 列）與 _log_re10_7_apply.json' % len(rows))
    return 0


if __name__ == '__main__':
    sys.exit(main())
