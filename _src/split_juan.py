
import io, os, re
base = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
src = os.path.join(base, 'TXT', '01_四分律刪繁補闕行事鈔.txt')
out = os.path.join(base, 'TXT_分卷')
os.makedirs(out, exist_ok=True)
lines = io.open(src, encoding='utf-8').read().split('\n')

markers = [(i, l.strip()) for i, l in enumerate(lines) if re.match(r'^【.*卷.+】$', l.strip())]
print('markers', len(markers))

HEAD = '四分律刪繁補闕行事鈔'
BASE = '底本：《大正新脩大藏經》第40冊 No.1804（CBETA）'

# front matter
front = lines[:markers[0][0]]
head_txt = '\n'.join([
    HEAD,
    BASE,
    '（本卷首：序、篇目）',
    '=' * 24,
    '',
]) + '\n'.join(front).strip() + '\n'
io.open(os.path.join(out, '00_卷首.txt'), 'w', encoding='utf-8').write(head_txt)

names = []
for n, (idx, mk) in enumerate(markers, start=1):
    end = markers[n][0] if n < len(markers) else len(lines)
    label = mk.strip('【】')          # 四分律刪繁補闕行事鈔卷上之一
    short = label.replace('四分律刪繁補闕行事鈔', '')   # 卷上之一
    body = [label] + lines[idx + 1:end]
    text = '\n'.join([
        HEAD + '　' + short,
        BASE,
        '（節自 01_四分律刪繁補闕行事鈔.txt）',
        '=' * 24,
        '',
    ]) + '\n'.join(body).strip() + '\n'
    fn = '%02d_%s.txt' % (n, short)
    io.open(os.path.join(out, fn), 'w', encoding='utf-8').write(text)
    names.append((fn, len(text)))

for fn, ln in names:
    print(fn, ln)
