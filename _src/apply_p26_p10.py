import io, os, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
T26 = io.open(os.path.join(B, '_src', 't_p26.txt'), encoding='utf-8').read().strip()
T10 = io.open(os.path.join(B, '_src', 't_p10.txt'), encoding='utf-8').read().strip()

# 篇26 鈔07：找譯文段（以「若法師」或「由大德說法教化」開頭）
out = os.path.join(B, 'AI語譯', 'out', '01_行事鈔')
done = False
for fn in os.listdir(out):
    fp = os.path.join(out, fn)
    tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(fp, encoding='utf-8').read()) if x.strip()]
    for i, t in enumerate(tt):
        if t.startswith('若法師者云') or t.startswith('若法師，應對他說') or ('由大德說法教化' in t and len(t) > 100 and '的' not in t):
            tt[i] = T26
            io.open(fp, 'w', encoding='utf-8').write('\n\n'.join(tt) + '\n')
            print('篇26 鈔07 已寫入', fn, i + 1)
            done = True
            break
    if done:
        break
if not done:
    print('篇26 找不到段')

# 篇10 記035：找資持記 out 中含「三正說儀，總示中」
out2 = os.path.join(B, 'AI語譯', 'out', '資持記')
done = False
for fn in os.listdir(out2):
    fp = os.path.join(out2, fn)
    tt = [x.strip() for x in re.split(r'\r?\n\r?\n', io.open(fp, encoding='utf-8').read()) if x.strip()]
    for i, t in enumerate(tt):
        if '三正說儀，總示中' in t:
            tt[i] = T10
            io.open(fp, 'w', encoding='utf-8').write('\n\n'.join(tt) + '\n')
            print('篇10 記035 已寫入', fn, i + 1)
            done = True
            break
    if done:
        break
if not done:
    print('篇10 找不到段')
