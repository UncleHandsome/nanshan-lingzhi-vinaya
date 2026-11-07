import os
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部\白話'
# 篇16 記122
d = Document(os.path.join(B, '會本_篇16_懺六聚法.docx'))
ps = [p.text.strip() for p in d.paragraphs]
for i, t in enumerate(ps):
    if t.startswith('【記122】'):
        print('TAG:', t[:60])
        print('BODY:', ps[i + 1][:160])
        break
# 空譯：找 tag 後 body 極短
for fn in ['會本_篇14_隨戒釋相.docx', '會本_篇15_持犯方軌.docx']:
    d = Document(os.path.join(B, fn))
    ps = [p.text.strip() for p in d.paragraphs]
    print('==', fn)
    cnt = 0
    for i, t in enumerate(ps):
        if t.startswith('【'):
            body = ps[i + 1] if i + 1 < len(ps) else ''
            if len(body) < 6:
                print(' ', t[:26], '| body:', repr(body))
                cnt += 1
                if cnt > 6:
                    break
