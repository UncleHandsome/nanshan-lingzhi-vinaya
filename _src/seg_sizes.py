
import io, os, re
base = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
books = [
 ('01', '四分律刪繁補闕行事鈔'),
 ('02', '四分律含注戒本疏'),
 ('03', '四分律刪補隨機羯磨疏'),
 ('04', '四分律比丘尼鈔'),
 ('05', '四分律拾毗尼義鈔'),
]
for num, title in books:
    p = os.path.join(base, 'TXT', '%s_%s.txt' % (num, title))
    lines = io.open(p, encoding='utf-8').read().split('\n')
    mk = [i for i, l in enumerate(lines) if re.match(r'^【.*卷.+】$', l.strip())]
    segs = []
    for n, i in enumerate(mk):
        j = mk[n+1] if n+1 < len(mk) else len(lines)
        txt = ''.join(lines[i:j])
        segs.append((lines[i].strip('【】'), len(re.sub(r'\s', '', txt))))
    print(num, title, 'segments', len(segs), 'total', sum(s[1] for s in segs))
    print('   ', ' | '.join('%s:%d' % (s[0].replace(title, ''), s[1]) for s in segs))
