# -*- coding: utf-8 -*-
"""sug.py NNN [NNN...] [--lim=N] [--all] -- compact actionable-item list from resp files.

Handles: numbered/bulleted items with 「old」→「new」, markdown table rows
(|原文|譯文|問題|), and "- 譯文：「…」 / - 建議：「…」" pairs.
Output (one line per distinct suggestion):
  MMMM idxCAT old ⇒ sug
CAT A=必改/修正/錯誤/嚴重, B=增譯/潤飾/加註/斟酌/體例/標點, C=其他.
Kept if --all, or HARD marker in item text, or cat==A.
"""
import os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RESP = os.path.join(ROOT, 'batch_qwen', 'r3')
LIM = 160
ALL = '--all' in sys.argv
for a in sys.argv[1:]:
    if a.startswith('--lim='):
        LIM = int(a[6:])
args = [a for a in sys.argv[1:] if not a.startswith('--')]
TAG = re.compile(r'【?\b(\d{3})-(\d{4})】?')
ITEM = re.compile(r'^\s*[（(]?(\d{1,2})[.、)）]')
BULL = re.compile(r'^\s*(?:[-*•·▪◎★☆❗⚠🔸🔹◆◇]|[①-⑳])')
PAIR = re.compile(r'「([^」]{1,60})」\s*(?:→|->|⇒|=>|應作|應改|宜作|宜改|改為|改譯|當作)\s*[「『]?([^」』|]{1,300})[」』]?')
QUOTE = re.compile(r'「([^」]{2,60})」')
HARD = re.compile(r'(誤|漏譯|漏|顛倒|講反|相反|矛盾|不通|脫漏|衍文|衍字|數目|數字|主語|不成句|錯字|錯誤|錯|脫|缺譯|失譯|未譯)')
SUG = re.compile(r'建議[^：:]{0,8}[：:]\s*(.+)')
SUGTAG = re.compile(r'(?:❌|⚠️?|★|應作|應改|宜作|宜改|改作|改為|建議改|建議作)\s*[：:]?\s*(.+)')
DASH = re.compile(r'[─–]{2,}\s*(.+)$')
ACAT = re.compile(r'(必改|應改|修正|錯誤|嚴重|需修|須改|要改|明確|硬傷|實質|較明確)')
BCAT = re.compile(r'(增譯|增義|潤飾|加註|補註|斟酌|體例|標點|小處|待查|存疑|可議|其他)')
SKIPHEAD = re.compile(r'^(建議|宜作|應作|改作|譯作|可改|宜改|註|注意|說明|理由|按語)')

def clean(s):
    return re.sub(r'`|^\s*#+\s*', '', s.replace('**', '')).strip()

def tidy(s, lim):
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'^[「『]', '', s)
    s = re.sub(r'[」』]。?$', '', s).strip()
    if lim and len(s) > lim:
        s = s[:lim] + '…'
    return s

def cells(row):
    return [c.strip() for c in row.strip().strip('|').split('|')]

def run(nnn):
    p = os.path.join(RESP, 'resp_%s.txt' % nnn)
    lines = [l.rstrip() for l in open(p, 'rb').read().decode('utf-8-sig').split('\n')]
    out, drop, cat, lab = [], 0, 'C', ''
    for i, ln in enumerate(lines):
        raw = ln.strip()
        s = clean(ln)
        if not s:
            continue
        m = TAG.search(s)
        if m:
            lab = m.group(1) + '-' + m.group(2)
        if raw.startswith('#') or (raw.startswith('**') and raw.endswith('**')
                                   and '「' not in raw and '→' not in raw and len(raw) < 80):
            cat = 'A' if ACAT.search(s) and not BCAT.search(s[:14]) else ('B' if BCAT.search(s) else 'C')
            continue
        if raw.startswith('|') and raw.count('|') >= 3:
            c = cells(raw)
            if len(c) < 3 or re.match(r'^[-: ]+$', c[0]) or c[0] in ('原文', '譯文') or c[2].startswith('問題'):
                continue
            old, q = c[1], c[2]
            ms = SUGTAG.search(q)
            sug = ms.group(1) if ms else q
            keep = ALL or bool(HARD.search(q)) or cat == 'A'
            if not keep or not old.strip():
                drop += 1
                continue
            out.append((lab, 'T', cat, tidy(old, 45), tidy(sug, LIM), tidy(c[0], 18)))
            continue
        s3 = re.sub(r'^[-*•·▪◎★☆❗⚠🔸🔹◆◇①-⑳]\s*', '', s)
        mi = ITEM.match(s3)
        if not mi and not BULL.match(s) and not PAIR.search(s):
            continue
        if SKIPHEAD.match(s3[:3]) and not PAIR.search(s):
            continue
        idx = mi.group(1) if mi else ''
        mp = PAIR.search(s)
        sug = ''
        nowx = ''
        for j in range(i, min(i + 4, len(lines))):
            s2 = clean(lines[j])
            s2b = re.sub(r'^[-*•·▪◎★☆❗⚠🔸🔹◆◇①-⑳]\s*', '', s2)
            if j > i and TAG.search(s2):
                break
            if j > i and (ITEM.match(s2b) or lines[j].strip().startswith('**')) and not SKIPHEAD.match(s2b[:3]):
                break
            mn = re.search(r'現譯[：:]?\s*[「『]([^」』]{2,90})', s2)
            if mn and not nowx:
                nowx = mn.group(1)
            ms = SUG.search(s2) if j > i else None
            if ms:
                sug = ms.group(1)
                break
        src = ''
        if mp:
            src, now = mp.group(1), mp.group(2)   # 原文 / 現譯
            sug = sug or now
        else:
            mq = QUOTE.search(s)
            now = mq.group(1) if mq else ''
        if nowx and (not now or len(nowx) > len(now)):
            now = nowx
        if not sug:
            ms = SUGTAG.search(s)
            if ms:
                sug = ms.group(1)
            else:
                md = DASH.search(s)
                if md:
                    sug = md.group(1)
        if not now and not sug:
            continue
        keep = ALL or bool(HARD.search(s)) or cat == 'A'
        if not keep:
            drop += 1
            continue
        out.append((lab, idx, cat, tidy(now, 62), tidy(sug, LIM), tidy(src, 18)))
    return out, drop

def merge(items):
    seen, res = {}, []
    for lab, idx, cat, now, sug, src in items:
        key = sug.strip()
        if key and key in seen:
            j = seen[key]
            if len(now) > len(res[j][3]):
                res[j] = (res[j][0], res[j][1], res[j][2], now, res[j][4], res[j][5])
            continue
        if key:
            seen[key] = len(res)
        res.append((lab, idx, cat, now, sug, src))
    return res

tot = 0
for a in args:
    nnn = a.zfill(3)
    its, drop = run(nnn)
    its = merge(its)
    tot += len(its)
    print('## %s keep=%d drop=%d items=%d' % (nnn, len(its), drop, len(its) + drop))
    if '--count' in sys.argv:
        continue
    for lab, idx, cat, now, sug, src in its:
        print(' %s %s%s %s%s ⇒ %s' % (lab, idx, cat, ('〔原:%s〕' % src) if src else '', now, sug))
if len(args) > 1:
    print('#TOTAL', tot)
