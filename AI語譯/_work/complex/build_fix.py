# -*- coding: utf-8 -*-
"""Classify complex-batch findings and build/validate/apply fixes."""
import json, os, sys, re, shutil, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
OUT = os.path.join(ROOT, 'AI語譯', '_work', 'complex')
sys.path.insert(0, OUT)
from pairs import parse_arrow

OVERRIDE = {
    42: [('三、不應親近諸比丘（不得與清淨比丘同輩伴侶親昵近住）', '三、應當親近（善）比丘')],
    44: [('順從而前來乞求', '順從而乞求')],
    66: [('俗男', '俗女')],
    87: [('未受戒者已出否？', '未受戒者已出')],
    106: [('〔註：原文作「閏月」〕', '')],
    386: [('房舍、床座等僧物；若問佛物，則指點佛塔旁的供具等', '房舍、床座等佛物，並指點佛塔旁的供具等')],
    628: [('李四替代了位置', '王替代了位置')],
    88: [('使受沙彌囑託之大僧得代受籌，亦', '')],
    176: [('便算舊物（可取來拼貼）', '便算舊物，即不須再貼')],
}
OTHER_BLACK = {13, 74, 76, 109, 113, 114, 137, 204, 206, 255, 479, 502, 517, 273, 274}
CHANGED_SEGS = {'01_行事鈔/01a_卷上之一#34', '01_行事鈔/01a_卷上之一#35', '01_行事鈔/01a_卷上之一#38'}

PUNCT_FIX = [('，）', '）'), ('、）', '）'), ('（，', '（'), ('，，', '，'), ('，。', '。'),
             ('，；', '；'), ('。，', '。'), ('；，', '；'), ('、，', '，'), ('，、', '、'),
             ('：，', '：'), ('，：', '：'), ('」。', '。」')]

def clean_text(t):
    for a, b in PUNCT_FIX:
        while a in t:
            t = t.replace(a, b)
    return t

def bal(t):
    return (t.count('（') - t.count('）'), t.count('「') - t.count('」'),
            t.count('《') - t.count('》'), t.count('〔') - t.count('〕'))

def norm(x):
    return re.sub(r'\s+', '', x or '')

QRE = re.compile(r'[「『]([^」』]{2,90})[」』]')

def fp_category(r):
    p = (r['ptype'] or '') + (r['problem'] or '')
    if '科判' in p or '科文' in p:
        return '誤解科判語'
    if r['label'] in CHANGED_SEGS:
        return '要求改回已修處'
    # quote only in 原文
    for q in QRE.findall(r['problem']):
        if norm(q) in norm(r['src']) and norm(q) not in norm(r['cur']):
            return '把【原文】當譯文'
    if any(k in p for k in ('語意', '表達', '通順', '生硬', '語氣')):
        return '只是表達不清'
    return '引文查無'

def main():
    apply_mode = '--apply' in sys.argv
    rows = json.load(open(os.path.join(OUT, 'rows.json'), encoding='utf-8'))
    live = [r for r in rows if 'OLD_IN_CUR' in r['flags']]
    other = [r for r in rows if 'OLD_IN_CUR' not in r['flags']]
    keep = json.load(open(os.path.join(OUT, 'other_keep.json'), encoding='utf-8'))
    keep_by_i = {k['i']: k for k in keep if k['i'] not in OTHER_BLACK}

    decisions = []
    seg_edits = collections.defaultdict(list)

    def add(r, tag, verdict, cat, old, new, note=''):
        decisions.append({'label': r['label'], 'tag': tag, 'verdict': verdict,
                          'cat': cat, 'old': old, 'new': new, 'note': note,
                          'pl': r['pl'], 'type': r['ptype'], 'conf': r['conf'],
                          'problem': r['problem'], 'sugg': r['sugg']})

    # live
    for i, r in enumerate(live, 1):
        tag = 'L%d' % i
        if i in OVERRIDE:
            for old, new in OVERRIDE[i]:
                add(r, tag, '真錯', '', old, new, 'override')
                seg_edits[r['label']].append((old, new, tag, True))
            continue
        tmp = r['cur']; applied = False
        for old, new in parse_arrow(r['sugg']):
            if not old or tmp.count(old) != 1:
                continue
            tmp = tmp.replace(old, new, 1)
            add(r, tag, '真錯', '', old, new)
            seg_edits[r['label']].append((old, new, tag, False))
            applied = True
        if not applied:
            add(r, tag, '真錯', '待套用', '', '', 'no usable pair')

    # other
    for i, r in enumerate(other, 1):
        tag = 'O%d' % i
        if i in keep_by_i:
            x = keep_by_i[i]
            old, new = x['old'], x['new']
            if r['cur'].count(old) == 1:
                add(r, tag, '真錯', '', old, new, 'other')
                seg_edits[r['label']].append((old, new, tag, False))
                continue
        qs = [q for q in QRE.findall(r['problem']) if norm(q) in norm(r['cur'])]
        qs.sort(key=len, reverse=True)
        if qs and len(qs[0]) >= 5:
            add(r, tag, '真錯', '待套用', '', '', 'criticized text persists, no safe edit')
            continue
        # gloss (括注) errors: criticized term sits inside a parenthetical gloss
        if any(k in (r['sugg'] or '') for k in ('括注', '夾注', '小注', '注作')):
            hit = False
            for q in QRE.findall(r['problem']):
                for mm in re.finditer(r'（[^）]{1,60}）', r['cur']):
                    if q and q in mm.group(0):
                        hit = True; break
                if hit:
                    break
            if hit:
                add(r, tag, '真錯', '待套用', '', '', 'gloss error, suggestion not A->B')
                continue
        if r['label'] in CHANGED_SEGS:
            add(r, tag, '已修', '', '', '')
            continue
        add(r, tag, '誤報', fp_category(r), '', '', '')

    # apply edits
    final = {}; problems = []
    curmap = {}
    for r in rows:
        curmap[r['label']] = r['cur']
    for lab, edits in seg_edits.items():
        cur = curmap.get(lab)
        if cur is None:
            problems.append((lab, 'no cur')); continue
        t = cur; b0 = bal(cur)
        for old, new, src, allrep in edits:
            n = t.count(old)
            if n < 1:
                problems.append((lab, src, old, n)); continue
            if n > 1 and not allrep:
                problems.append((lab, src, 'multi', n)); continue
            t = t.replace(old, new) if allrep else t.replace(old, new, 1)
        t = clean_text(t)
        if bal(t) != b0:
            problems.append((lab, 'balance changed', b0, bal(t)))
        if t.strip() != cur.strip():
            final[lab] = t
    st = collections.Counter(d['verdict'] for d in decisions)
    print('decisions', st)
    print('真錯 待套用', sum(1 for d in decisions if d['verdict'] == '真錯' and d['cat'] == '待套用'))
    print('誤報 cats', collections.Counter(d['cat'] for d in decisions if d['verdict'] == '誤報'))
    print('segments changed', len(final), 'problems', len(problems))
    for p in problems[:15]:
        print('  ', p)
    json.dump({'final': final, 'decisions': decisions, 'problems': problems},
              open(os.path.join(OUT, 'build.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    if apply_mode:
        apply_fixes(final)

def apply_fixes(final):
    byfile = collections.defaultdict(dict)
    for lab, text in final.items():
        m = re.match(r'(.+?)/([^/]+)#(\d+)$', lab)
        byfile[(m.group(1), m.group(2))][int(m.group(3))] = text
    bakroot = os.path.join(ROOT, '歸檔', 'complex批修正前')
    changed = []
    for (book, chunk), segs in sorted(byfile.items()):
        src = os.path.join(ROOT, 'AI語譯', 'out', book, chunk + '.txt')
        raw = open(src, 'rb').read(); text = raw.decode('utf-8')
        eol = '\r\n' if '\r\n' in text else '\n'
        blocks = re.split(re.escape(eol + eol), text)
        for s, newtext in segs.items():
            assert s - 1 < len(blocks), (book, chunk, s)
            blocks[s - 1] = newtext
        bak = os.path.join(bakroot, book)
        os.makedirs(bak, exist_ok=True)
        if not os.path.exists(os.path.join(bak, chunk + '.txt')):
            shutil.copy2(src, os.path.join(bak, chunk + '.txt'))
        open(src, 'wb').write((eol + eol).join(blocks).encode('utf-8'))
        changed.append([book, chunk, len(segs)])
    print('files written', len(changed))
    json.dump(changed, open(os.path.join(OUT, 'applied.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    for c in changed[:10]:
        print('  ', c)

if __name__ == '__main__':
    main()
