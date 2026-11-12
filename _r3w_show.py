import sys, json, os
sys.path.insert(0, r'C:\Users\lionc\OneDrive\桌面\XW\三大部')
from _r3w_lib import *

m = json.load(open(os.path.join(BASE, '_map.json'), encoding='utf-8'))
want = sys.argv[1:]
for r in m:
    if not want or str(r['num']) in want or r['id'] in want:
        cur = para_of(read_text(r['book'], r['chunk']), r['para'])
        print('=' * 8, r['id'], r['book'] + '/' + r['chunk'], '#' + str(r['para']))
        print('[原]', r['src'])
        print('[今]', cur)
        print()
