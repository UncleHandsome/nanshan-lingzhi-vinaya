# -*- coding: utf-8 -*-
"""Notes for fix_r8b_g2 round: per-row disposition."""
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')

rows = json.loads(io.open(r'AI語譯\_work\review\_g2_rows.json', encoding='utf-8').read())

APPLIED = {1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 26, 27, 31, 49}
SHIFT = {3, 24}
FIXED = {28, 29, 30, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 50, 51, 52}

out = []
out.append('report_r8b — g2 (資持記 / 02_戒疏 / 01_行事鈔) 處理紀錄')
out.append('共 52 列；輸出 18 段（23 列合併）；跳過 29 列。')
out.append('')
for i, r in enumerate(rows, 1):
    if i in FIXED:
        tag = 'FIX  -> 輸出（%s %s#%s）' % (r['book'], r['chunk'], r['seg'])
    elif i in APPLIED:
        tag = 'SKIP -> 已套用（問題句不在 current）'
    elif i in SHIFT:
        tag = 'SKIP -> 報告 orig 與段號錯位（current 屬該段且無問題）'
    else:
        tag = '??'
    out.append('[%02d] %s %s#%s %s' % (i, r['gid'], r['chunk'], r['seg'], tag))
    out.append('     ' + r['problem'][:90])
out.append('')
out.append('特殊說明：')
out.append('1) [03] 287-0034：報告 orig=15b#18、seg 標 19（current 為 287-0035 的註文）。真正的 15b#18 譯文已是「這名比丘便前往織師的住處…」，無「私自」，無須改。')
out.append('2) [24] 466-0021：報告 orig 為 15b#63，seg 卻標 15c#1（current 為 466-0022「《增一》二像」段，內容正確）。466-0021 的正確譯文已存在於 out/資持記/15b_下三.txt 第 63 段，無須改。此列 P0 為標籤錯位造成的誤報。')
out.append('3) [47] 672-0008：16a#53 原譯整段抄自 #52，已依 TXT_分卷/資持記_細分/16a_下四.txt 第 58 行原文重譯（含〔舊云表眾不一…〕夾注）。')
out.append('4) [37] 670-0004：僅依 suggestion 改「責令賠償」→「責令加倍償還」；其後「價值與原借貸之物相當」保留，因記文原文即作「與本相當者」，未便改動。')
out.append('5) [43]-[46] 672-0006 同一段四條合併為一段；[32][33]、[37][38]、[48][49] 亦同段合併（[49] 已套用，僅併入 [48] 的修改）。')
io.open(r'AI語譯\_work\review\_r8b_g2_notes.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('ok', len(out))
