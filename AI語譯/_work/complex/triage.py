# -*- coding: utf-8 -*-
"""Mechanical triage of complex-batch findings."""
import re, json, os, sys, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
OUT = os.path.join(ROOT, 'AI語譯', '_work', 'complex')

def load():
    S = json.load(open(os.path.join(OUT, 'segidx.json'), encoding='utf-8'))
    cur = json.load(open(os.path.join(OUT, 'cur.json'), encoding='utf-8'))
    items = json.load(open(os.path.join(OUT, 'items.json'), encoding='utf-8'))
    return S['labels'], S['codes'], cur, items

Q = '「([^」]{2,60})」'
QUOTE_RE = re.compile(Q)

def parse_arrow(sugg):
    """Return list of (old,new) pairs from a 建議 string."""
    pairs = []
    if not sugg:
        return pairs
    s = sugg.replace('**', '')
    # 「A」→「B」  / 「A」→ Ｂ
    for m in re.finditer(r'「([^」]{1,80})」\s*[→➜]\s*「?([^」。；\n]{0,80})」?', s):
        pairs.append((m.group(1), m.group(2).strip()))
    # 將「A」改為「B」 / 「A」改為「B」 / 「A」改作「B」
    for m in re.finditer(r'「([^」]{1,80})」\s*(?:改為|改作|改成|應改為)\s*「?([^」。；\n]{0,80})」?', s):
        pairs.append((m.group(1), m.group(2).strip()))
    # 改為「B」（no old）
    if not pairs:
        m = re.search(r'(?:改為|改作|改成|作)\s*「([^」]{1,120})」', s)
        if m:
            pairs.append(('', m.group(1)))
    # 刪除「A」/刪「A」/刪去「A」
    for m in re.finditer(r'刪(?:除|去|掉)?\s*「([^」]{1,60})」', s):
        pairs.append((m.group(1), ''))
    # dedupe preserve order
    seen = set(); out = []
    for p in pairs:
        if p not in seen:
            seen.add(p); out.append(p)
    return out

def norm(x):
    return re.sub(r'\s+', '', x or '')

def main():
    labels, codes, cur, items = load()
    rows = []
    stats = collections.Counter()
    for it in items:
        if it['section'] != 'find':
            continue
        lab = it['label']
        rec = labels.get(lab)
        c = cur.get(lab, '')
        src = rec['src'] if rec else ''
        start = norm(it.get('原文起首', ''))
        prob = it.get('問題', '') or ''
        sugg = it.get('建議', '') or ''
        basis = it.get('依據', '') or ''
        pairs = parse_arrow(sugg)
        flags = []
        if rec is None:
            flags.append('NOLABEL')
        # start match
        if start:
            if start in norm(src):
                pass
            elif start[:10] in norm(src):
                flags.append('START_PART')
            else:
                flags.append('START_MISS')
        # arrow pairs
        old_in_cur = new_in_cur = old_in_src = False
        old_found = []
        for old, new in pairs:
            o, n = norm(old), norm(new)
            if o and o in norm(c):
                old_in_cur = True; old_found.append(old)
            if n and n in norm(c):
                new_in_cur = True
            if o and o in norm(src):
                old_in_src = True
        if pairs:
            if old_in_cur:
                flags.append('OLD_IN_CUR')          # still unfixed
            elif new_in_cur:
                flags.append('ALREADY_FIXED')       # change applied
            else:
                flags.append('NEITHER')
        # quotes in 問題 that look like 譯文 quotes
        quotes = QUOTE_RE.findall(prob)
        q_cur = sum(1 for q in quotes if norm(q) in norm(c))
        q_src = sum(1 for q in quotes if norm(q) in norm(src))
        if quotes and q_cur == 0 and q_src == 0:
            flags.append('QUOTE_NOWHERE')
        if quotes and q_cur == 0 and q_src > 0 and old_in_src:
            flags.append('MAYBE_SRC_AS_TR')
        rows.append({'file': it['file'], 'code': it['code'], 'label': lab, 'pl': it['pl'], 'ptype': it['ptype'],
                     'conf': (it.get('信心', '') or '')[:1], 'flags': ','.join(flags),
                     'nquote': len(quotes), 'qcur': q_cur, 'qsrc': q_src,
                     'pairs': len(pairs), 'start': it.get('原文起首', ''), 'problem': prob,
                     'basis': basis, 'sugg': sugg, 'src': src, 'cur': c})
        for f in flags:
            stats[f] += 1
    json.dump(rows, open(os.path.join(OUT, 'rows.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('rows', len(rows))
    for k, v in stats.most_common():
        print(k, v)
    print('pl', collections.Counter(r['pl'] for r in rows))

if __name__ == '__main__':
    main()
