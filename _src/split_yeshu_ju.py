
# -*- coding: utf-8 -*-
import io, os, re
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
VAR = {'牀':'床','説':'說','衆':'眾','爲':'為','敎':'教','卽':'即','旣':'既','竝':'並'}
def nh(ch): return VAR.get(ch, ch)
def han(s): return ''.join(nh(ch) for ch in s if '\u4e00' <= ch <= '\u9fff' or ch == '〇')
book = han(io.open(os.path.join(D,'03_四分律刪補隨機羯磨疏_句讀_clean.txt'), encoding='utf-8').read())
S = os.path.join(D,'TXT_分卷','03_業疏')
J = os.path.join(D,'TXT_句讀','03_業疏')
os.makedirs(J, exist_ok=True)
files = sorted([f for f in os.listdir(S) if f.endswith('.txt')], key=lambda x: (0 if x.startswith('00_') else 1, x))
starts = []
for f in files:
    raw = io.open(os.path.join(S,f), encoding='utf-8').read().split('\n')[5:]
    sp = [x.strip() for x in raw if x.strip()]
    first = han(sp[0])[:16]
    pos = book.find(first)
    starts.append((f, pos))
ok = 0
for i, (f, pos) in enumerate(starts):
    if pos < 0: print('miss start', f); continue
    end = starts[i+1][1] if i+1 < len(starts) and starts[i+1][1] > pos else len(book)
    # 以「漢字索引」切回原文
    idx = [k for k, ch in enumerate(book) if '\u4e00' <= ch <= '\u9fff' or ch == '〇']
    # pos 是漢字序，需轉 raw
    raw_all = io.open(os.path.join(D,'03_四分律刪補隨機羯磨疏_句讀_clean.txt'), encoding='utf-8').read()
    # 重新以 raw 切：用 raw 中漢字計數定位
    def raw_of(n):
        c = 0
        for k, ch in enumerate(raw_all):
            if '\u4e00' <= ch <= '\u9fff' or ch == '〇':
                c += 1
                if c == n: return k + 1
        return len(raw_all)
    a = raw_of(pos); b = raw_of(end) if end < len(book) else len(raw_all)
    seg = raw_all[a:b]
    # 依空行切段，寫入 5 行抬頭 + 段落
    paras = [x.strip() for x in re.split(r'\n\s*\n', seg) if x.strip()]
    head = ['四分律刪補隨機羯磨疏　' + f[:-4].split('_',1)[1], '底本：CBETA（卍續藏 X41n0728）', '（句讀版）', '=' * 24, '']
    io.open(os.path.join(J, f), 'w', encoding='utf-8').write('\n'.join(head) + '\n' + '\n\n'.join(paras) + '\n')
    ok += 1
print('written', ok, 'of', len(files))
