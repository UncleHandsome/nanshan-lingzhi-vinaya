
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
THRESH = 30000

def nchars(s):
    return len(re.sub(r'\s', '', s))

def find_split(lines, start, end, target):
    cum = 0; best = start
    for k in range(start, end):
        cum += nchars(lines[k])
        if cum >= target:
            best = k; break
    # prefer a 篇 heading within +-40 lines
    pat = re.compile(r'^\s*\S+篇第[一二三四五六七八九十]+')
    cand = None
    for d in range(0, 41):
        for k in (best - d, best + d):
            if start < k < end and pat.match(lines[k]):
                cand = k; break
        if cand is not None:
            break
    return cand if cand is not None else best

def write(path, title, short, srcname, body, suffix=''):
    head = '\n'.join([
        title + '　' + short + suffix,
        '底本：CBETA 電子佛典（大正藏／卍續藏）',
        '（節自 %s）' % srcname,
        '=' * 24,
        '',
    ])
    io.open(path, 'w', encoding='utf-8').write(head + '\n'.join(body).strip() + '\n')

if os.path.isdir(outroot):
    shutil.rmtree(outroot)
os.makedirs(outroot)

for num, title, folder in books:
    srcdir = os.path.join(outroot, folder)
    os.makedirs(srcdir)
    src = os.path.join(base, 'TXT', '%s_%s.txt' % (num, title))
    srcname = os.path.basename(src)
    lines = io.open(src, encoding='utf-8').read().split('\n')
    mk = [i for i, l in enumerate(lines) if re.match(r'^【.*卷.+】$', l.strip())]
    # front matter
    write(os.path.join(srcdir, '00_卷首.txt'), title, '卷首', srcname, lines[:mk[0]])
    for n, i in enumerate(mk, start=1):
        j = mk[n] if n < len(mk) else len(lines)
        label = lines[i].strip('【】')
        short = label[label.find('卷'):]
        body = lines[i:j]
        total = nchars('\n'.join(body))
        if total > THRESH:
            half = total // 2
            k = find_split(lines, i, j, half)
            part1 = [label] + lines[i+1:k]
            part2 = [label + '（續）'] + lines[k:j]
            write(os.path.join(srcdir, '%02da_%s.txt' % (n, short)), title, short + '（前半）', srcname, part1)
            write(os.path.join(srcdir, '%02db_%s.txt' % (n, short)), title, short + '（後半）', srcname, part2)
            print('%s %02d %s SPLIT at line %d (%d/%d)' % (folder, n, short, k, nchars('\n'.join(part1)), total))
        else:
            write(os.path.join(srcdir, '%02d_%s.txt' % (n, short)), title, short, srcname, body)

for root, dirs, files in os.walk(outroot):
    dirs.sort(); files.sort()
    print(os.path.basename(root) or 'TXT_分卷', len(files))
