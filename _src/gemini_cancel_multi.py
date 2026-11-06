import io, os, json, urllib.request, urllib.error

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
KEY = os.environ.get('GEMINI_API_KEY', '')
fp = os.path.join(B, 'AI語譯', '_work', 'gemini_jobs_multi.json')
if not os.path.exists(fp):
    print('沒有提交紀錄（未建立 job）')
else:
    reg = json.load(io.open(fp, encoding='utf-8'))
    print('已記錄 job', len(reg))
    for k, name in reg.items():
        url = 'https://generativelanguage.googleapis.com/v1beta/%s:cancel' % name
        req = urllib.request.Request(url, data=b'{}', headers={
            'Content-Type': 'application/json', 'x-goog-api-key': KEY}, method='POST')
        try:
            urllib.request.urlopen(req, timeout=60).read()
            print('cancelled', k, name)
        except Exception as e:
            print('cancel fail', k, e)
