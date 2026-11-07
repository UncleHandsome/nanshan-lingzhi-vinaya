import csv, sys, textwrap, json, os

BASE = os.path.dirname(os.path.abspath(__file__))
REP = os.path.join(BASE, 'report_t2_located.tsv')
APP = os.path.join(BASE, 'applied_t2_located.tsv')

def load():
    rows = list(csv.DictReader(open(REP, encoding='utf-8'), delimiter='\t'))
    ap = set((r['book'], r['chunk'], r['seg']) for r in csv.DictReader(open(APP, encoding='utf-8'), delimiter='\t'))
    na = [r for r in rows if (r['book'], r['chunk'], r['seg']) not in ap]
    return na

def dump(lo, hi, width=60, out=None):
    na = load()
    buf = []
    for i in range(lo, min(hi, len(na))):
        r = na[i]
        buf.append('=== %d | %s | %s | %s | %s | %s ===' % (i, r['book'], r['chunk'], r['seg'], r['level'], r['cls']))
        buf.append('PROBLEM: ' + r['problem'])
        buf.append('SUGGESTION: ' + r['suggestion'])
        buf.append('TR: ' + r['tr'])
        buf.append('CURRENT:')
        cur = r['current']
        for j in range(0, len(cur), width):
            buf.append('%5d| %s' % (j, cur[j:j+width]))
        buf.append('')
    txt = '\n'.join(buf)
    if out:
        open(os.path.join(BASE, out), 'w', encoding='utf-8').write(txt)
        print('wrote', out, len(txt))
    else:
        sys.stdout.write(txt)

def show(i, width=60):
    na = load()
    r = na[i]
    print('=== %d | %s | %s | %s | %s | %s ===' % (i, r['book'], r['chunk'], r['seg'], r['level'], r['cls']))
    print('PROBLEM: ' + r['problem'])
    print('SUGGESTION: ' + r['suggestion'])
    print('TR: ' + r['tr'])
    print('CURRENT:')
    cur = r['current']
    for j in range(0, len(cur), width):
        print('%5d| %s' % (j, cur[j:j+width]))

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'dump':
        dump(int(sys.argv[2]), int(sys.argv[3]), out=sys.argv[4] if len(sys.argv) > 4 else None)
    elif cmd == 'show':
        show(int(sys.argv[2]))
