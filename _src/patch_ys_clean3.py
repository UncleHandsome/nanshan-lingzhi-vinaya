import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\site_ju.py'
lines = io.open(p, encoding='utf-8').read().split('\n')
out = []
skip = False
for i, l in enumerate(lines):
    if l.strip() == "o = o.strip('*').lstrip()":
        indent = l[:len(l) - len(l.lstrip())]
        out.append(indent + "o = o.strip('*').lstrip()")
        out.append(indent + "m3 = re.search(r'【[疏記]】', o)")
        out.append(indent + "if m3 and m3.start() > 0:")
        out.append(indent + "    o = o[m3.start():]")
        continue
    if l.strip().startswith("m2 = re.match") or l.strip().startswith("rest = o[len") \
       or l.strip().startswith("j2 = rest.find") or l.strip().startswith("if 0 <= j2") \
       or l.strip().startswith("o = rest[j2:]") or l.strip() == "if m2:":
        continue
    if l.strip() == "if ytags and 0 <= gi < len(ytags) and ytags[gi] and not o.startswith('【'):":
        indent = l[:len(l) - len(l.lstrip())]
        out.append(indent + "if ytags and 0 <= gi < len(ytags) and ytags[gi] and not o.startswith('【'):")
        continue
    if l.strip() == "if not o.startswith('【'):":
        continue
    out.append(l)
io.open(p, 'w', encoding='utf-8').write('\n'.join(out))
print('trim-before-tag patched')
