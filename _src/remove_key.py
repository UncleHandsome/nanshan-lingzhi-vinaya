import io, os, re, glob

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
for f in ['gemini_submit.py', 'gemini_submit_multi.py', 'gemini_poll.py', 'gemini_cancel.py', 'gemini_cancel_multi.py']:
    p = os.path.join(B, '_src', f)
    if not os.path.exists(p):
        continue
    s = io.open(p, encoding='utf-8').read()
    s = re.sub(r"KEY\s*=\s*'[^']+'", "KEY = os.environ.get('GEMINI_API_KEY', '')", s)
    if 'import io, os' not in s and 'import os' not in s:
        s = s.replace('import io,', 'import io, os,', 1)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('masked', f)
