import io, os, glob, json, shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
AD = os.path.join(B, 'AI語譯', '_work', 'align_ai')
AD2 = os.path.join(B, 'AI語譯', '_work', 'align_ai2')

missing = []
for f in sorted(glob.glob(os.path.join(AD, '[0-9][0-9][0-9].json'))):
    n = os.path.basename(f)[:3]
    out = os.path.join(AD, 'out_%s.json' % n)
    if not os.path.exists(out) or os.path.getsize(out) < 50:
        missing.append(f)
print('missing', len(missing), [os.path.basename(x) for x in missing])
if os.path.isdir(AD2):
    shutil.rmtree(AD2)
os.makedirs(AD2)
man = []
for i, f in enumerate(missing, 1):
    dst = os.path.join(AD2, '%03d.json' % i)
    shutil.copyfile(f, dst)
    man.append(dict(new='%03d' % i, orig=os.path.basename(f)[:3]))
json.dump(man, io.open(os.path.join(AD2, 'manifest.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('prepared', len(man))
