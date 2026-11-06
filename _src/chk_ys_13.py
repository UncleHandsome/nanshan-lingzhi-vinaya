import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '03_業疏')
T = os.path.join(B, 'AI語譯', 'out', '03_業疏')
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))
for k in ['13a_卷三之二', '13b_卷三之二', '14a_卷三之三']:
    sp = [x.strip() for x in io.open(os.path.join(S, k + '.txt'), encoding='utf-8').read().split('\n')[5:] if x.strip()]
    tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(os.path.join(T, k + '.txt'), encoding='utf-8').read()) if x.strip()]
    print('=====', k, len(sp), len(tt))
    print(' sp0 :', sp[0][:36])
    print(' tt0 :', tt[0][:36])
    # 搜 sp0 開頭 10 字在哪些 tt
    probe = han(sp[0])[:10]
    hits = [j for j, t in enumerate(tt) if probe in han(t)]
    print(' sp0 出現在 tt:', hits[:5])
    print(' sp末:', sp[-1][:36])
    print(' tt末:', tt[-1][:36])
