from docx import Document
import re, sys, os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = sys.argv[1] if len(sys.argv) > 1 else '04'
fs = [f for f in os.listdir(os.path.join(B, '白話')) if f.startswith('會本_篇%s_' % p) and f.endswith('.docx')]
d = Document(os.path.join(B, '白話', fs[0]))
ps = [x.text.strip() for x in d.paragraphs]
cur = ''
for i, t in enumerate(ps):
    m = re.match(r'^【鈔(\d+)】(.+)$', t)
    if m:
        cur = '鈔%s｜%s' % (m.group(1), re.sub(r'\s+', '', m.group(2))[:36])
        print('\n' + cur)
        continue
    m = re.match(r'^【記(\d+)[^】]*】(.+)$', t)
    if m and cur:
        print('   記%-4s %s' % (m.group(1), re.sub(r'\s+', '', m.group(2))[:60]))
