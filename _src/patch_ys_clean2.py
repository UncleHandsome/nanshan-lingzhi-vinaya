import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\site_ju.py'
lines = io.open(p, encoding='utf-8').read().split('\n')
out = []
for i, l in enumerate(lines):
    if l.strip() == "if ytags and 0 <= gi < len(ytags) and ytags[gi] and not o.startswith('【'):":
        indent = l[:len(l) - len(l.lstrip())]
        out.append(indent + "o = o.strip('*').lstrip()")
        out.append(indent + "m2 = re.match(r'^(【[疏記]】)', o)")
        out.append(indent + "if m2:")
        out.append(indent + "    rest = o[len(m2.group(1)):]")
        out.append(indent + "    j2 = rest.find(m2.group(1))")
        out.append(indent + "    if 0 <= j2 <= 12:")
        out.append(indent + "        o = rest[j2:]")
    if l.strip() == "o = ytags[gi] + o":
        indent = l[:len(l) - len(l.lstrip())]
        out.append(indent + "if not o.startswith('【'):")
        out.append(indent + "    o = ytags[gi] + o")
        continue
    out.append(l)
io.open(p, 'w', encoding='utf-8').write('\n'.join(out))
print('clean block inserted')
