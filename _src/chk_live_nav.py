import urllib.request, json, io

b = 'https://unclehandsome.github.io/nanshan-lingzhi-vinaya/'
t = urllib.request.urlopen(b + 'nav.json?x=12', timeout=40).read().decode('utf-8')
d = json.loads(t)
for bk in d['books']:
    if bk['out'] == 'yeshu':
        print('live yeshu volumes:')
        for v in bk['vols']:
            print(' ', v['v'], [s[1] for s in v['secs']])

loc = json.load(io.open(r'docs\nav.json', encoding='utf-8'))
for bk in loc['books']:
    if bk['out'] == 'yeshu':
        print('local yeshu volumes:')
        for v in bk['vols']:
            print(' ', v['v'], [s[1] for s in v['secs']])
