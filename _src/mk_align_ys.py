# -*- coding: utf-8 -*-
"""業疏：每分塊一批，讓 AI 把「句讀行」對到「分卷行」。"""
import io, os, re, json

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '03_業疏')
T = os.path.join(B, 'AI語譯', 'out', '03_業疏')
J = os.path.join(B, 'TXT_句讀', '03_業疏')
OUT = os.path.join(B, 'AI語譯', '_work', 'align_ys')
han = lambda s: ''.join(re.findall(r'[\u4e00-\u9fff]', s))


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        os.remove(os.path.join(OUT, f))
    n = 0
    for f in sorted(os.listdir(S)):
        if not f.endswith('.txt'):
            continue
        k = f[:-4]
        jp = os.path.join(J, k + '.txt')
        if not os.path.exists(jp):
            continue
        sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        ju = [x.strip() for x in io.open(jp, encoding='utf-8').read().split('\n') if x.strip()]
        # 去掉檔頭
        BAD = ('四分律', '（', '===', '南山三大部', '底本：')
        while ju and any(ju[0].startswith(x) for x in BAD):
            ju = ju[1:]
        if not sp or not ju:
            continue
        n += 1
        items = [dict(i=i, text=x[:80]) for i, x in enumerate(ju)]
        cand = [dict(c=c, text=x[:80]) for c, x in enumerate(sp)]
        io.open(os.path.join(OUT, '%03d.json' % n), 'w', encoding='utf-8').write(json.dumps(
            dict(key=k, items=items, cand=cand), ensure_ascii=False, indent=1))
    print('batches', n)


if __name__ == '__main__':
    main()
