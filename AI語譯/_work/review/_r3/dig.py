# -*- coding: utf-8 -*-
"""dig.py NNN [NNN ...] -- compact digest: block map + condensed resp.

Filtering: drop decorative lines; drop whole sections whose heading is 潤飾/總結/
清單/小結/優先/綜合/通則/體例 (keeping only lines with hard-error markers);
drop pure-polish item blocks; collapse blank lines.
"""
import os, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
RESP = os.path.join(ROOT, 'batch_qwen', 'r3')
WORK = os.path.join(ROOT, 'AI語譯', '_work', 'review', '_r3')
BLK = json.load(open(os.path.join(WORK, 'blocks.json'), encoding='utf-8'))

TAG = re.compile(r'【(\d{3})-(\d{4})】')
HARD = re.compile(r'(誤|漏|顛倒|講反|相反|矛盾|不通|脫漏|衍文|衍字|主語|錯|應改|應作|宜改|宜作|改為|改譯|補足|補譯|刪去|贅|重複|數目|數字|引文|不成句)')
SOFT = re.compile(r'(潤飾|語感|語氣|通順|可留可刪|不必改|斟酌|小問題|僅供參考|已可|尚可|無誤|沒問題|無需|不影響義理|可刪可留|略可|些微)')
DROP_LINE = re.compile(r'^(-{3,}|\*{3,})\s*$')
DROP_SEC = re.compile(r'(潤飾|總結|清單|小結|優先|綜合建議|通則建議|通用建議|體例建議|附註|說明$)')
HEAD = re.compile(r'^\s*(#{1,4}\s*|[一二三四五六七八九十]+[、.]|（[一二三四五六七八九十]+）|[0-9]+\.[、]?|[★☆❗⚠✏⭕○●❶❷❸❹❺].{0,6}$)')

def is_head(ln):
    s = ln.strip()
    return bool(s) and (s[0] in '#一二三四五六七八九十（(★☆❗⚠✏⭕○●❶❷❸❹❺' or re.match(r'^\d+\.', s))

OUTD = os.path.join(ROOT, 'AI語譯', 'out')
_cache = {}

def paras(book, chunk):
    k = (book, chunk)
    if k not in _cache:
        t = open(os.path.join(OUTD, book, chunk + '.txt'), 'rb').read().decode('utf-8-sig')
        _cache[k] = [(i, s.rstrip('\r')) for i, s in enumerate(t.split('\n')) if s.rstrip('\r').strip()]
    return _cache[k]

def locate(b):
    ps = paras(b['book'], b['chunk'])
    tr = (b['tr'] or '').strip()
    exact = [i for i, (li, s) in enumerate(ps) if s.strip() == tr]
    if len(exact) == 1:
        return exact[0], True
    import difflib
    best = (0, 0.0)
    for i, (li, s) in enumerate(ps):
        r = difflib.SequenceMatcher(None, s, tr).ratio()
        if r > best[1]:
            best = (i, r)
    return best[0], False

ADDNOTE = re.compile(r'(加注|補注|宜註|註明|注為|注：|可注|宜注|加註|小傳|全稱|釋名|標明|補一句|補一注)')
HARD2 = re.compile(r'(誤|漏|顛倒|矛盾|錯|不通|脫漏|衍)')

def condense(t):
    lines = [ln.rstrip() for ln in t.split('\n')]
    out = []
    dropping = False
    for ln in lines:
        s = ln.strip()
        if not s or DROP_LINE.match(s):
            continue
        s2 = re.sub(r'\*\*|`|^\s*#+\s*', '', s)
        if s2.startswith('✏') or '✏️' in s2:
            continue
        if ADDNOTE.search(s2) and not HARD2.search(s2):
            continue
        if is_head(s2) and DROP_SEC.search(s2):
            dropping = True
            continue
        if is_head(s2) and not DROP_SEC.search(s2):
            dropping = False
        if dropping and not (HARD.search(s2) and '建議改譯' not in s2):
            continue
        out.append(s2)
    txt = '\n'.join(out)
    txt = re.sub(r'\n{2,}', '\n', txt)
    # item blocks: drop polish-only blocks
    parts = re.split(r'(?=【\d{3}-\d{4}】)', txt)
    keep = []
    for seg in parts:
        if TAG.search(seg) and SOFT.search(seg) and not HARD.search(seg):
            m = TAG.findall(seg)
            keep.append('[潤飾略] ' + ' '.join('%s-%s' % x for x in m))
            continue
        keep.append(seg.strip())
    return '\n'.join(x for x in keep if x)

def show(nnn):
    blks = [b for b in BLK if b['nnn'] == nnn]
    info = []
    for b in blks:
        try:
            pi, same = locate(b)
        except Exception:
            pi, same = -1, False
        info.append('%s#%s%s' % (b['mmmm'], b['seg'], '' if same else '!out%s' % (pi + 1)))
    print('## %s  n=%d  %s' % (nnn, len(blks),
          ' '.join(sorted(set('%s/%s' % (b['book'], b['chunk']) for b in blks)))))
    print('   ' + ' '.join(info))
    t = open(os.path.join(RESP, 'resp_%s.txt' % nnn), 'rb').read().decode('utf-8-sig')
    print(condense(t))

for a in sys.argv[1:]:
    show(a.zfill(3))
