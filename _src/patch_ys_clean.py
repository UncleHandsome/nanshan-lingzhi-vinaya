import io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = B + r'\_src\site_ju.py'
s = io.open(p, encoding='utf-8').read()
old = """            if ytags and 0 <= gi < len(ytags) and ytags[gi] and not o.startswith('【'):
                o = ytags[gi] + o"""
new = """            o = o.strip('*').lstrip()
            m2 = re.match(r'^(【[疏記]】)', o)
            if m2:
                rest = o[len(m2.group(1)):]
                j2 = rest.find(m2.group(1))
                if 0 <= j2 <= 12:
                    o = rest[j2:]
            if ytags and 0 <= gi < len(ytags) and ytags[gi] and not o.startswith('【'):
                o = ytags[gi] + o"""
if old in s and 'j2' not in s:
    s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('slice clean patched')
else:
    print('already or missing')
