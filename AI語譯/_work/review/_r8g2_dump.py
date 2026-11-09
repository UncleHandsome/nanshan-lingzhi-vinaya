import csv, sys, textwrap
sys.stdout.reconfigure(encoding='utf-8')
p = 'AI語譯/_work/review/_r8g2_rows.tsv'
with open(p, encoding='utf-8', newline='') as f:
    rows = list(csv.DictReader(f, delimiter='\t'))
print('rows', len(rows))
out = open('AI語譯/_work/review/_r8g2_dump.txt', 'w', encoding='utf-8')
for row in rows:
    out.write('=' * 100 + '\n')
    out.write('RIDX %s  GID %s  BOOK %s  CHUNK %s  SEG %s  LV %s  CLS %s\n' % (
        row['ridx'], row['gid'], row['book'], row['chunk'], row['seg'], row['level'], row['cls']))
    out.write('--- PROBLEM ---\n')
    out.write('\n'.join(textwrap.wrap(row['problem'], 100)) + '\n')
    out.write('--- SUGGESTION ---\n')
    out.write('\n'.join(textwrap.wrap(row['suggestion'], 100)) + '\n')
    out.write('--- ORIG ---\n')
    out.write('\n'.join(textwrap.wrap(row['orig'], 100)) + '\n')
    out.write('--- CURRENT (len=%d) ---\n' % len(row['current']))
    out.write('\n'.join(textwrap.wrap(row['current'], 100)) + '\n')
out.close()
print('dumped')
for row in rows:
    print(row['ridx'], row['gid'], row['book'], row['chunk'], row['seg'], 'curlen=%d' % len(row['current']))
