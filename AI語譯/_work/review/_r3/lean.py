# -*- coding: utf-8 -*-
"""lean.py NNN [...] -- ultra-compact action list from resp files.

Keeps only lines that carry a concrete verdict/suggestion, plus their immediate
continuation (quote lines / following bullets indented under it). Drops prose
explanation, 加註 requests, 潤飾 notes and summary sections.
"""
import os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RESP = os.path.join(ROOT, 'batch_qwen', 'r3')
WORK = os.path.join(ROOT, 'AI語譯', '_work', 'review', '_r3')
BLK = __import__('json').load(open(os.path.join(WORK, 'blocks.json'), encoding='utf-8'))

ACT = re.compile(r'(→|應改|必改|應作|宜改|宜作|改譯|改為|❌|誤|漏譯|顛倒|矛盾|錯|不通|脫漏|衍|贅|增譯|增字|刪)')
ADD = re.compile(r'(加注|補注|宜註|註明|注為|可注|宜注|加註|小傳|全稱|補一句|補一注|標明)')
TAG = re.compile(r'【(\d{3})-(\d{4})】')

def show(nnn):
    blks = [b for b in BLK if b['nnn'] == nnn]
    print('## %s n=%d %s' % (nnn, len(blks), ' '.join(sorted(set(b['book'] + '/' + b['chunk'] for b in blks)))))
    print('  ' + ' '.join('%s#%s' % (b['mmmm'], b['seg']) for b in blks))
    t = open(os.path.join(RESP, 'resp_%s.txt' % nnn), 'rb').read().decode('utf-8-sig')
    lines = [l.rstrip() for l in t.split('\n')]
    out, i = [], 0
    curtag = ''
    while i < len(lines):
        s = lines[i].strip()
        if not s or re.match(r'^(-{3,}|\*{3,})$', s):
            i += 1; continue
        m = TAG.search(s)
        if m:
            curtag = m.group(1) + '-' + m.group(2)
        s2 = re.sub(r'\*\*|`|^\s*#+\s*', '', s)
        keep = bool(ACT.search(s2)) and not (ADD.search(s2) and not re.search(r'(誤|漏|顛倒|矛盾|錯|不通)', s2))
        if keep:
            out.append('%s %s' % (curtag if curtag else '', s2))
            # absorb following quote/continuation lines
            j = i + 1
            while j < len(lines):
                n = lines[j].strip()
                if not n:
                    j += 1; continue
                if n.startswith('>') or n.startswith(('　', '  ')) or n.startswith(('- ', '* ')):
                    out.append('    ' + re.sub(r'^\*\*|`', '', n))
                    j += 1
                else:
                    break
            i = j
            continue
        i += 1
    print('\n'.join(out))

for a in sys.argv[1:]:
    show(a.zfill(3))
