import glob, os, io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
needles = ['引經佛在說法', '晡即申時', '出要，即證理', '崇，猶重也']
for f in sorted(glob.glob(os.path.join(B, 'AI語譯', 'out', '01_行事鈔', '*.txt'))):
    tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(f, encoding='utf-8').read()) if x.strip()]
    for i, t in enumerate(tt):
        for nd in needles:
            if nd in t:
                print(os.path.basename(f), i, nd, '|', t[:60])
