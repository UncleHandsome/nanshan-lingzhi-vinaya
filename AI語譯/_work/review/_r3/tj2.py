# -*- coding: utf-8 -*-
"""tj2.py NNN [...] -- triage, compact: only L items + full 原 for live blocks.
L = cited text still in current 譯文 (needs judgement). F skipped, S/G listed short."""
import os, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RESP = os.path.join(ROOT, 'batch_qwen', 'r3')
MAT = os.path.join(ROOT, '校閱_10K')
LBL = re.compile(r'^【(\d{3})-(\d{4})】(.+?)/(.+?)#(\d+)\s*$')
ACT = re.compile(r'(→|應改|必改|應作|宜改|宜作|改譯|改為|❌|誤|漏譯|顛倒|矛盾|錯|不通|脫漏|衍|贅|增譯|增字|刪)')
ADD = re.compile(r'(加注|補注|宜註|註明|注為|可注|宜注|加註|小傳|全稱|補一句|補一注|標明)')
TAG = re.compile(r'【(\d{3})-(\d{4})】')
Q = re.compile(r'「([^」]{2,80})」')

def read(p):
    return open(p, 'rb').read().decode('utf-8-sig')

def parse_mat(nnn):
    blocks, cur = [], None
    for ln in read(os.path.join(MAT, '校閱_%s.txt' % nnn)).split('\n'):
        ln = ln.rstrip('\r')
        m = LBL.match(ln)
        if m:
            cur = {'label': m.group(1) + '-' + m.group(2), 'book': m.group(3),
                   'chunk': m.group(4), 'src': '', 'tr': ''}
            blocks.append(cur); continue
        if cur is None: continue
        if ln.startswith('【原文】'): cur['src'] = ln[4:]
        elif ln.startswith('【譯文】'): cur['tr'] = ln[4:]
    return blocks

def lean_lines(nnn):
    t = read(os.path.join(RESP, 'resp_%s.txt' % nnn))
    lines = [l.rstrip() for l in t.split('\n')]
    out, curtag = [], ''
    for s0 in lines:
        s = s0.strip()
        if not s or re.match(r'^(-{3,}|\*{3,})$', s):
            continue
        m = TAG.search(s)
        if m: curtag = m.group(1) + '-' + m.group(2)
        s2 = re.sub(r'\*\*|`|^\s*#+\s*', '', s)
        keep = bool(ACT.search(s2)) and not (ADD.search(s2) and not re.search(r'(誤|漏|顛倒|矛盾|錯|不通)', s2))
        if keep:
            out.append((curtag, s2))
    return out

def main():
    for a in sys.argv[1:]:
        nnn = a.zfill(3)
        blocks = parse_mat(nnn)
        bylab = {b['label']: b for b in blocks}
        lines = lean_lines(nnn)
        F, S, G, L = [], [], [], []
        print('######## %s blocks=%d lean=%d  %s' % (nnn, len(blocks), len(lines),
              ' '.join(b['book'] + '/' + b['chunk'] + '#' + b['label'][-4:] for b in blocks)))
        liveblocks = collections.OrderedDict()
        for tag, s in lines:
            parts = re.split(r'(?:→|->|⇒|——)', s)
            olds = Q.findall(parts[0])
            news = Q.findall(parts[1]) if len(parts) > 1 else []
            blk = bylab.get(tag) or (blocks[0] if blocks else None)
            tr = blk['tr'] if blk else ''
            src = blk['src'] if blk else ''
            hit = [o for o in olds if o in tr]
            hit = [o for o in hit if not any(n.startswith(o) or (o in n and len(n) > len(o)) for n in news)]
            if not olds:
                continue
            if hit:
                L.append((tag, s, hit, blk, tr))
                if blk: liveblocks.setdefault(blk['label'], blk)
                continue
            if any(n in tr for n in news):
                F.append(tag); continue
            alt = None
            for b in blocks:
                if any(o in b['tr'] for o in olds):
                    alt = b; break
            if alt:
                L.append((tag, s, [o for o in olds if o in alt['tr']], alt, alt['tr']))
                liveblocks.setdefault(alt['label'], alt)
                continue
            if any(o in src for o in olds):
                S.append((tag, s)); continue
            G.append((tag, s))
        for tag, s, hit, blk, tr in L:
            print('[L] %s | %s' % (tag, s[:260]))
            for o in hit:
                k = tr.find(o)
                print('    {%s} …%s…' % (o, tr[max(0, k-45):k+len(o)+45]))
        print('  totals: L=%d F=%d S=%d G=%d' % (len(L), len(F), len(S), len(G)))
        if F: print('  F:', ' '.join(F))
        for tag, s in S:
            print('  [S] %s | %s' % (tag, s[:130]))
        for tag, s in G:
            print('  [G] %s | %s' % (tag, s[:130]))
        for lab, b in liveblocks.items():
            print('  == %s %s/%s' % (lab, b['book'], b['chunk']))
            print('     原:', b['src'][:1400])

main()
