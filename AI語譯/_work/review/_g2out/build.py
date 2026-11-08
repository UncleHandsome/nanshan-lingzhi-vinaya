# -*- coding: utf-8 -*-
import json, difflib, collections

SEL = json.load(open('AI語譯/_work/review/_g2out/sel.json', encoding='utf-8'))
rows = json.load(open('AI語譯/_work/review/_g2out/out_rows.json', encoding='utf-8'))
# rows: [idx, chunk, seg, new]

# apply sequentially; merge rows that target the same (chunk, seg)
merged = collections.OrderedDict()
order = []
for idx, chunk, seg, new in rows:
    key = (chunk, seg)
    if key not in merged:
        merged[key] = new
        order.append(key)
    else:
        # re-apply this row's ops on the merged text is not possible generically;
        # instead verify both derive from the same base and keep later text
        # (handled by construction: ops are disjoint for duplicate pairs)
        merged[key] = new

# Detect duplicate groups where the two source currents are identical
groups = collections.defaultdict(list)
for idx, chunk, seg, new in rows:
    groups[(chunk, seg)].append(idx)
dups = {k: v for k, v in groups.items() if len(v) > 1}
print('duplicate groups:', dups)

# Rebuild duplicates properly: apply union of ops on the shared base
import importlib.util, sys
spec = importlib.util.spec_from_file_location('opsmod', 'AI語譯/_work/review/_g2out/ops.py')
# ops.py executes printing; just re-read OPS by exec with suppressed output
src = open('AI語譯/_work/review/_g2out/ops.py', encoding='utf-8').read()
src = src.split('OUT = []')[0]
ns = {'json': json, 'SEL': SEL}
exec(compile(src, 'ops', 'exec'), ns)
OPS = ns['OPS']

final = collections.OrderedDict()
for key, idxs in groups.items():
    if len(idxs) == 1:
        final[key] = merged[key]
        continue
    base = SEL[idxs[0]]['current']
    for j in idxs:
        assert SEL[j]['current'] == base, (key, 'base mismatch')
    new = base
    for j in idxs:
        mode, payload = OPS[j]
        if mode == 'edit_all':
            for old, rep in payload:
                new = new.replace(old, rep)
        elif mode == 'edit':
            for old, rep in payload:
                assert new.count(old) == 1, (j, old[:30], new.count(old))
                new = new.replace(old, rep, 1)
        else:
            raise SystemExit('unexpected full in dup group %s' % (key,))
    final[key] = new.rstrip()

# write TSV
out = []
for (chunk, seg), new in final.items():
    assert '\n' not in new and '\t' not in new and new
    out.append('01_行事鈔\t%s\t%s\t%s' % (chunk, seg, new))

with open('AI語譯/_work/review/fix_parts_g2.tsv', 'w', encoding='utf-8', newline='') as f:
    f.write('\n'.join(out) + '\n')

print('output rows:', len(out))
print('skipped report rows:', len(SEL) - sum(len(v) for v in groups.values()))

# diff audit
rep = []
for key, idxs in groups.items():
    base = SEL[idxs[0]]['current'].rstrip()
    new = final[key]
    if base == new:
        rep.append('NOCHANGE %s' % (key,))
        continue
    sm = difflib.SequenceMatcher(None, base, new, autojunk=False)
    chunks = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        chunks.append('%s: [%s] -> [%s]' % (tag, base[i1:i2][:80], new[j1:j2][:80]))
    rep.append('%r %s\n    %s' % (key, '', '\n    '.join(chunks)))
open('AI語譯/_work/review/_g2out/diffaudit.txt', 'w', encoding='utf-8').write('\n'.join(rep))
print('audit written')
