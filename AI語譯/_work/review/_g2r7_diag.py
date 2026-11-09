import csv, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
p = 'AI語譯/_work/review/_g2r7_rows.tsv'
rows = list(csv.DictReader(open(p, encoding='utf-8', newline=''), delimiter='\t'))
print('rows', len(rows))

pat = re.compile(r'「([^」]+)」[^「」]{0,6}?(?:改為|改作|改称|改成|換成|换成|易為)[^「」]{0,6}?「([^」]+)」')
n_quote = 0
n_applied = 0
applied = []
noq = []
for r in rows:
    s = r['suggestion']
    cur = r['current']
    m = pat.search(s)
    if m:
        n_quote += 1
        if m.group(1) not in cur:
            n_applied += 1
            applied.append((r['ridx'], r['chunk'], r['seg'], m.group(1), m.group(2)))
    else:
        noq.append((r['ridx'], r['chunk'], r['seg'], s[:80]))
print('simple 將「A」改為「B」:', n_quote, 'A-not-in-current:', n_applied)
print('--- not-simple suggestion count:', len(noq))
for x in noq[:40]:
    print(x)
print('--- applied candidates')
for x in applied[:40]:
    print(x)
# length of current
lens = [len(r['current']) for r in rows]
print('cur len min/median/max', min(lens), sorted(lens)[len(lens)//2], max(lens), 'sum', sum(lens))
