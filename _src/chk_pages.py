import urllib.request, json

for u in ['https://api.github.com/repos/UncleHandsome/nanshan-lingzhi-vinaya/pages/builds/latest',
          'https://api.github.com/repos/UncleHandsome/nanshan-lingzhi-vinaya/pages']:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'check'})
        r = urllib.request.urlopen(req, timeout=30)
        d = json.loads(r.read().decode('utf-8'))
        print(u.split('/')[-1], r.status)
        for k in ['status', 'created_at', 'updated_at', 'commit', 'url', 'html_url', 'build_type', 'source']:
            if k in d:
                print('  ', k, d[k])
    except Exception as e:
        print(u, 'ERR', e)
