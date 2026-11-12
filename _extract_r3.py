import re, io

s = open(r'待跑_審查擋掉\rere.txt', encoding='utf-8-sig').read()
lines = s.splitlines()
r3 = lines[2108:3668]
open('_r3_rere.txt', 'w', encoding='utf-8', newline='\n').write('\n'.join(r3))
print('lines', len(r3), 'chars', sum(len(x) for x in r3))
