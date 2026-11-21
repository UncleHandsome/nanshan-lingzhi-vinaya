# -*- coding: utf-8 -*-
"""pack_audit 審後拆回：每包只把被 [n] 點名的成員標 FIX，其餘 PASS。"""
import io
import json
import os
import re
import shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
P = os.path.join(B, '測試', '重譯', '資持記', '_打包審核')
OUT = os.path.join(B, '測試', '重譯', '資持記', '_終審_拆回', '回覆')
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT, exist_ok=True)


def verdict(t):
    m = re.search(r'【結論】\s*(PASS|FIX|ERROR)', t)
    return m.group(1) if m else ('FIX' if 'FIX' in t else 'PASS')


def hard_section(t):
    m = re.search(r'【必改硬傷】\s*(.*?)(?:\n【|\Z)', t, re.S)
    return m.group(1).strip() if m else ''


def split_fixes(sec, members):
    # 只看行首的 [n]，且支援 [2][3] / [2,3] / [2-3]
    marks = list(re.finditer(r'(?m)^[ \t]*(?:[-*•][ \t]*)?((?:\[(?:打包段附)?\[?\d+\]?\]\s*)+)', sec))
    out = {}
    spans = []
    if not marks:
        return out, False
    for i, m in enumerate(marks):
        nums = [int(x) for x in re.findall(r'\d+', m.group(1))]
        end = marks[i + 1].start() if i + 1 < len(marks) else len(sec)
        body = sec[m.end():end].strip()
        spans.append((m.start(), end))
        for n in nums:
            if 1 <= n <= len(members) and body:
                out.setdefault(members[n - 1], []).append(body)
    # 有未標 [n] 的條目（行首 bullet）→ 整包安全退路
    uncovered = []
    pos = 0
    for a, b in spans:
        uncovered.append(sec[pos:a])
        pos = b
    uncovered.append(sec[pos:])
    leftover = '\n'.join(uncovered)
    fallback = bool(re.search(r'(?m)^\s*[-*•]\s*\S', leftover))
    return out, fallback


packs = 0
pass_n = fix_n = 0
fallback_n = 0
for f in sorted(os.listdir(P)):
    if not f.endswith('.json'):
        continue
    key = f[:-5]
    rp = os.path.join(P, '回覆', key + '_回.txt')
    if not os.path.exists(rp):
        continue
    x = json.load(io.open(os.path.join(P, f), encoding='utf-8'))
    members = [str(m) for m in (x.get('members') or [])]
    if not members:
        continue
    t = io.open(rp, encoding='utf-8').read()
    v = verdict(t)
    packs += 1
    # 單成員：可能是 packed=True 的子段包，整份原樣搬，不拆裡面的 [n]
    if len(members) == 1:
        k = members[0]
        io.open(os.path.join(OUT, k + '_回.txt'), 'w', encoding='utf-8').write(t)
        if v == 'FIX':
            fix_n += 1
        else:
            pass_n += 1
        continue
    if v == 'PASS':
        for k in members:
            io.open(os.path.join(OUT, k + '_回.txt'), 'w', encoding='utf-8').write('【結論】\nPASS\n\n【必改硬傷】\n無\n')
            pass_n += 1
        continue
    sec = hard_section(t)
    fixes, fallback = split_fixes(sec, members)
    if not fixes or fallback:
        fallback_n += 1
        for k in members:
            fixes.setdefault(k, []).append(sec or '未標 [n] 的硬傷，整包保留 FIX')
    for k in members:
        if k in fixes:
            io.open(os.path.join(OUT, k + '_回.txt'), 'w', encoding='utf-8').write('【結論】\nFIX\n\n【必改硬傷】\n' + '\n'.join(fixes[k]) + '\n')
            ev = os.path.join(P, '回覆', key + '_evid.json')
            if os.path.exists(ev):
                shutil.copy(ev, os.path.join(OUT, k + '_evid.json'))
            fix_n += 1
        else:
            io.open(os.path.join(OUT, k + '_回.txt'), 'w', encoding='utf-8').write('【結論】\nPASS\n\n【必改硬傷】\n無\n')
            pass_n += 1
print('packs', packs, 'pass', pass_n, 'fix', fix_n, 'fallback', fallback_n, 'out', OUT)
