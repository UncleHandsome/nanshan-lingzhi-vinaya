import io, os, json, urllib.request, urllib.error

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
KEY = os.environ.get('GEMINI_API_KEY', '')
WORK = os.path.join(B, 'AI語譯', '_work')
meta = json.load(io.open(os.path.join(WORK, 'gemini_batch.json'), encoding='utf-8'))
name = meta['name']
print('job', name)

for action in ['cancel']:
    url = 'https://generativelanguage.googleapis.com/v1beta/%s:%s' % (name, action)
    req = urllib.request.Request(url, data=b'{}', headers={
        'Content-Type': 'application/json', 'x-goog-api-key': KEY}, method='POST')
    try:
        r = urllib.request.urlopen(req, timeout=120)
        d = json.loads(r.read().decode('utf-8'))
        print('OK', action, json.dumps(d, ensure_ascii=False)[:400])
    except urllib.error.HTTPError as e:
        print('FAIL', action, e.code, e.read().decode('utf-8', 'ignore')[:300])
    except Exception as e:
        print('FAIL', action, e)

# 再查狀態
url = 'https://generativelanguage.googleapis.com/v1beta/%s' % name
req = urllib.request.Request(url, headers={'x-goog-api-key': KEY})
try:
    d = json.loads(urllib.request.urlopen(req, timeout=120).read().decode('utf-8'))
    st = d.get('metadata', {}).get('state')
    stats = d.get('metadata', {}).get('batchStats', {})
    print('state now', st, stats)
except Exception as e:
    print('poll err', e)
