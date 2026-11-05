
import io, os, re, shutil
base = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
outroot = os.path.join(base, 'TXT_分卷')
books = [
 ('01', '四分律刪繁補闕行事鈔', '01_行事鈔'),
 ('02', '四分律含注戒本疏', '02_戒疏'),
 ('03', '四分律刪補隨機羯磨疏', '03_業疏'),
 ('04', '四分律比丘尼鈔', '04_比丘尼鈔'),
 ('05', '四分律拾毗尼義鈔', '05_拾毗尼義鈔'),
]
LIMIT = 30000  # bytes per chunk, keep under 32K

def b(s):
    return len(s.encode('utf-8'))

def parts_for(lines, start, end):
    total = b('\n'.join(lines[start:end]))
    n = max(1, -(-total // LIMIT))
    if n == 1:
        return [(start, end)]
    target = total / n
    bounds = [start]
    cum = 0
    for k in range(start, end):
        cum += b(lines[k]) + 1
        if len(bounds) < n and cum >= target * len(bounds):
            bounds.append(k)
    bounds.append(end)
    # dedupe / ensure monotonic
    res = []
    for i in range(len(bounds) - 1):
        a, z = bounds[i], bounds[i+1]
        if z > a:
            res.append((a, z))
    return res

def write(path, title, label, srcname, body, idx=None, tot=None):
    suffix = ''
    if tot and tot > 1:
        suffix = '（%d/%d）' % (idx, tot)
    head = '\n'.join([
        title + '　' + label + suffix,
        '底本：CBETA 電子佛典（大正藏／卍續藏）',
        '（節自 %s）' % srcname,
        '=' * 24,
        '',
    ])
    io.open(path, 'w', encoding='utf-8').write(head + '\n'.join(body).strip() + '\n')

if os.path.isdir(outroot):
    shutil.rmtree(outroot)
os.makedirs(outroot)
summary = []

for num, title, folder in books:
    srcdir = os.path.join(outroot, folder)
    os.makedirs(srcdir)
    src = os.path.join(base, 'TXT', '%s_%s.txt' % (num, title))
    srcname = os.path.basename(src)
    lines = io.open(src, encoding='utf-8').read().split('\n')
    mk = [i for i, l in enumerate(lines) if re.match(r'^【.*卷.+】$', l.strip())]
    write(os.path.join(srcdir, '00_卷首.txt'), title, '卷首', srcname, lines[:mk[0]])
    cnt = 0
    for n, i in enumerate(mk, start=1):
        j = mk[n] if n < len(mk) else len(lines)
        label = lines[i].strip('【】')
        short = label[label.find('卷'):]
        segs = parts_for(lines, i, j)
        for t, (a, z) in enumerate(segs, start=1):
            body = ([label] if t == 1 else [label + '（續）']) + lines[a+1 if t == 1 else a:z]
            letter = '' if len(segs) == 1 else chr(96 + t)
            fn = '%02d%s_%s.txt' % (n, letter, short)
            write(os.path.join(srcdir, fn), title, short, srcname, body,
                  idx=t, tot=len(segs))
            cnt += 1
    summary.append((folder, cnt + 1))

for f, c in summary:
    print(f, c)
print('total', sum(c for _, c in summary))
