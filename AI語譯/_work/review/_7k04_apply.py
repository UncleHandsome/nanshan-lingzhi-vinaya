import json, sys, io

sys.stdout.reconfigure(encoding='utf-8')
spec = json.load(open(sys.argv[1], encoding='utf-8'))
path = spec['file']
data = open(path, 'rb').read()
crlf = b'\r\n' in data
text = data.decode('utf-8-sig')
nl = '\r\n' if crlf else '\n'
ok = 0
for i, pair in enumerate(spec['edits'], 1):
    old, new = pair[0], pair[1]
    if crlf:
        old = old.replace('\n', '\r\n')
        new = new.replace('\n', '\r\n')
    c = text.count(old)
    if c != 1:
        print('FAIL edit#%d count=%d :: %s' % (i, c, old[:40]))
        sys.exit(2)
    text = text.replace(old, new)
    ok += 1
open(path, 'wb').write(text.encode('utf-8'))
print('OK %s edits=%d crlf=%s' % (path, ok, crlf))
