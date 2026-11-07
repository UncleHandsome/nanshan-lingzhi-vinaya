import io, os
from docx import Document

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
HB = ['卷上之一', '卷上之二', '卷上之三', '卷上之四', '卷中之一', '卷中之二', '卷中之三', '卷中之四',
      '卷下之一', '卷下之二', '卷下之三', '卷下之四']
probes = ['古科列名在十門之首', '釋結界篇結謂白二限約', '第30篇', '諸部別行']
for vol in HB:
    d = Document(os.path.join(B, '白話', '行事鈔資持記句級合編_%s.docx' % vol))
    ts = [p.text.strip() for p in d.paragraphs]
    stats = {q: sum(q in t for t in ts) for q in probes}
    heads = [t for t in ts if t.startswith('第') and '篇' in t][:3]
    print('%-6s 段%5d  %s  篇首=%s' % (vol, len(ts), stats, heads))
