import re, sys, os
p = r'待跑_審查擋掉\rere.txt'
raw = open(p,'rb').read()
print('bytes', len(raw))
print('CRLF', raw.count(b'\r\n'), 'LF', raw.count(b'\n'), 'CR', raw.count(b'\r'))
s = raw.decode('utf-8-sig')
print('chars', len(s))
print('has \r\n in str:', s.count('\r\n'), 'count \n:', s.count('\n'))
lines = s.splitlines()
print('lines', len(lines))
for n,l in enumerate(lines,1):
    if re.match(r'^\s*#{1,4}\s', l):
        print(n, repr(l[:110]))
