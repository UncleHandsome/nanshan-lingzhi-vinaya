import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '03_業疏')
T = os.path.join(B, 'AI語譯', 'out', '03_業疏')
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))
k = '13a_卷三之二'
tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(os.path.join(T, k + '.txt'), encoding='utf-8').read()) if x.strip()]
probe = han(tt[0])[:12]
print('tt0 probe:', probe)
for kk in ['12b_卷三之一', '13a_卷三之二', '13b_卷三之二', '14a_卷三之三', '12a_卷三之一']:
    sp = [x.strip() for x in io.open(os.path.join(S, kk + '.txt'), encoding='utf-8').read().split('\n')[5:] if x.strip()]
    # 白話是譯文，原文不可能含白話；改為搜 sp 的漢字是否出現在 tt 全文中
    tth = han(''.join(tt))
    sph = han(sp[0])[:10]
    print(kk, 'sp0在tt中:', sph in tth, '| sp0:', sp[0][:26])
