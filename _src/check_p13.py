import importlib.util, os, re, collections, io

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
spec = importlib.util.spec_from_file_location('ex', os.path.join(B, '_src', 'export_materials.py'))
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
sec = ex.sections()[12]
ch = [it[0] for it in sec['items'] if not re.match(r'^\d+\s*[一-鿿]{2,10}篇', it[0].strip())]
print('篇13 鈔數', len(ch))
c = collections.Counter(ch)
print('重複段落', [(k[:20], v) for k, v in c.items() if v > 1][:5])
sp = [x.strip() for x in io.open(os.path.join(B, 'TXT_分卷', '01_行事鈔'), encoding='utf-8')] if False else None
# 檢查 13a out 對齊
kp = os.path.join(B, 'TXT_分卷', '01_行事鈔')
for f in sorted(os.listdir(kp)):
    if f.startswith('13'):
        print('chunk', f)
        s = [x.strip() for x in io.open(os.path.join(kp, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        t = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(os.path.join(B, 'AI語譯', 'out', '01_行事鈔', f), encoding='utf-8').read()) if x.strip()]
        print(' sp', len(s), 'tt', len(t))
        print('  sp0:', s[0][:40])
        print('  tt0:', t[0][:40] if t else 'NA')
