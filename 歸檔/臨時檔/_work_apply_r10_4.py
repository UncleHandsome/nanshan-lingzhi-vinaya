# -*- coding: utf-8 -*-
"""套用 re10_4（001 檔第 4 輪）已判定修正。

只改 3 段：#7、#8、#52（00_卷首）。
輸出：fix_re10_4.tsv、_log_re10_4_apply.json、備份 歸檔/re10_4修正前/
"""
import io, os, re, json, shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SRC = os.path.join(B, 'AI語譯', 'out', '01_行事鈔', '00_卷首.txt')
BK = os.path.join(B, '歸檔', 're10_4修正前', '01_行事鈔', '00_卷首.txt')
FIX = os.path.join(B, 'AI語譯', '_work', 'review', 'fix_re10_4.tsv')
LOG = os.path.join(B, 'AI語譯', '_work', 'review', '_log_re10_4_apply.json')

# (段序, 段號, 類型, 判定, A, B, 摘要)
ITEMS = [
    (7, '001-0007', '術語錯', '真錯',
     '至於彰顯實行世事、作為後學軌範的',
     '至於彰顯世間合行之律儀法事、作為後學軌範的',
     '「世事」＝世中合行之事（非世俗事務），補出律儀法事'),
    (8, '001-0008', '術語錯', '真錯',
     '全都收攬為本宗的一家正見（定見），用以救濟初學者的耗費工夫！',
     '全都總攬於本宗之中而得於此一處備見，用以救濟初學者的耗費工夫！',
     '「攬為此宗之一見」＝收歸本宗、一處備見，非「一家正見（定見）」'),
    (52, '001-0052', '術語錯', '真錯',
     '五是起心作意（或情狀）的虛妄與屬實。',
     '五是能起之心與所對之境的差互與相應（心境虛實）。',
     '「起情虛實」＝心境相應為實、差互為虛，非「起心作意」之虛妄／屬實'),
]

SKIP = [
    (7, '001-0007', '術語錯', '誤報', '「文在義集」照譯與記相符（記：「以羯磨文散在廣律，並以義類集結成篇，故云文在義集」），建議語與現譯幾同義'),
    (8, '001-0008', '主詞或施受關係錯', '誤報', '「用濟新學之費功」現譯雖澀，義仍為免除新學費功，屬表達不順非義誤'),
    (63, '001-0063', '術語錯', '誤報', '「前事」可指當前所秉法事（記：「正羯磨時白告警策等，亦名理有而成前事也」），現譯係第 1 輪依此改定，不宜回改為「前述之事」'),
]


def main():
    raw = io.open(SRC, encoding='utf-8', newline='').read()
    segs = raw.split('\r\n\r\n')
    assert len(segs) == 83, len(segs)
    os.makedirs(os.path.dirname(BK), exist_ok=True)
    if not os.path.exists(BK):
        shutil.copy2(SRC, BK)
    old = list(segs)
    log = []
    for n, sid, typ, verdict, a, b, note in ITEMS:
        i = n - 1
        assert segs[i].count(a) == 1, (n, segs[i].count(a))
        assert b not in segs[i], ('B already present', n)
        segs[i] = segs[i].replace(a, b)
        log.append(dict(seg=n, sid=sid, type=typ, verdict=verdict, a=a, b=b,
                        note=note, before=old[i], after=segs[i]))
    new = '\r\n\r\n'.join(segs)
    io.open(SRC, 'w', encoding='utf-8', newline='').write(new)
    # 驗證
    chk = io.open(SRC, encoding='utf-8', newline='').read().split('\r\n\r\n')
    for n, sid, typ, verdict, a, b, note in ITEMS:
        assert a not in chk[n - 1] and b in chk[n - 1]
    changed = [i for i in range(len(segs)) if segs[i] != old[i]]
    print('changed segments (1-based):', [i + 1 for i in changed])
    assert changed == [6, 7, 51], changed
    assert len(chk) == 83
    # TSV
    with io.open(FIX, 'w', encoding='utf-8', newline='') as fh:
        for i in changed:
            fh.write('%s\t%s\t%d\t%s\n' % ('01_行事鈔', '00_卷首', i + 1, segs[i]))
    json.dump(dict(source='測試_80K對照/10_4.txt', applied=len(ITEMS),
                   backup='歸檔/re10_4修正前/01_行事鈔/00_卷首.txt',
                   items=log), io.open(LOG, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('fix rows:', len(changed), 'log ok')


if __name__ == '__main__':
    main()
