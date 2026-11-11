# -*- coding: utf-8 -*-
"""re10_6 套用：備份 → 逐句最小替換 → 寫 fix_re10_6.tsv / _log_re10_6_apply.json。"""
import io, os, shutil, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, 'AI語譯', 'out', '01_行事鈔', '00_卷首.txt')
BAK_DIR = os.path.join(B, '歸檔', 're10_6修正前', '01_行事鈔')
REV = os.path.join(B, 'AI語譯', '_work', 'review')

REPL = [
    dict(seg=5, sid='001-0005', type='主詞或施受關係錯',
         a='的人，是必須仔細考評審度才能得見的（言其極為罕見）。',
         b='，（前代）何曾有人能對此詳加考評審察呢（言前代皆未論及）！',
         note='者為提頓，可得詳而評之為反詰；記云「蓋言不能詳評故也」'),
    dict(seg=41, sid='001-0041', type='科判語誤譯',
         a='第一，說明教法興起的用意。至人（佛陀）出現於世',
         b='第一門：序教興意。一、為大慈愍物：至人（佛陀）出現於世',
         note='門名獨立；首意「大慈」補為一，免與第二門序號衝突'),
    dict(seg=41, sid='001-0041', type='科判語誤譯',
         a='第二，是為了對治外道',
         b='二、是為了對治外道',
         note='門內三意之二，非第二門'),
    dict(seg=41, sid='001-0041', type='科判語誤譯',
         a='第三，是為了對辨其他宗派',
         b='三、是為了對辨其他宗派',
         note='門內三意之三，非第三門'),
    dict(seg=46, sid='001-0046', type='術語錯',
         a='層層重複的開許（重聽）',
         b='嚴加禁制與隨機開許（重與聽）',
         note='重＝制教止持（zhòng），聽＝約行作持；記云「重聽通收二種」'),
]


def main():
    raw = io.open(SRC, 'rb').read()
    txt = raw.decode('utf-8')
    assert '\r\n' in txt
    before_segs = txt.split('\r\n\r\n')

    for r in REPL:
        n = txt.count(r['a'])
        assert n == 1, (r['seg'], r['a'], n)
        txt = txt.replace(r['a'], r['b'])
        r['before'] = before_segs[r['seg'] - 1]
        print('OK seg%-3d %s -> %s' % (r['seg'], r['a'][:20], r['b'][:20]))

    after_segs = txt.split('\r\n\r\n')
    for r in REPL:
        r['after'] = after_segs[r['seg'] - 1]

    # 備份（byte 級）
    os.makedirs(BAK_DIR, exist_ok=True)
    bak = os.path.join(BAK_DIR, '00_卷首.txt')
    shutil.copyfile(SRC, bak)
    print('backup', bak, os.path.getsize(bak))

    io.open(SRC, 'w', encoding='utf-8', newline='').write(txt)
    print('written', SRC, os.path.getsize(SRC))

    # fix_re10_6.tsv（書/book、chunk、段序、修正後段全文）
    rows, seen = [], set()
    for r in REPL:
        if r['seg'] in seen:
            continue
        seen.add(r['seg'])
        rows.append('01_行事鈔\t00_卷首\t%d\t%s' % (r['seg'], r['after']))
    tsv = os.path.join(REV, 'fix_re10_6.tsv')
    io.open(tsv, 'w', encoding='utf-8', newline='').write('\r\n'.join(rows) + '\r\n')
    print('tsv', tsv, len(rows), 'rows')

    log = dict(source='測試_80K對照/10_6.txt', applied=len(rows),
               backup='歸檔/re10_6修正前/01_行事鈔/00_卷首.txt', items=REPL)
    io.open(os.path.join(REV, '_log_re10_6_apply.json'), 'w', encoding='utf-8').write(
        json.dumps(log, ensure_ascii=False, indent=1))
    print('log ok; segs', len([s for s in after_segs if s.strip()]))


if __name__ == '__main__':
    main()
