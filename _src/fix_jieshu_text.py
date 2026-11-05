import os, io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
S = os.path.join(B, 'TXT_分卷', '02_戒疏')
T = os.path.join(B, 'AI語譯', 'out', '02_戒疏')

REPL_SRC = [
    ('終南大一山', '終南太一山'),
    ('乃是是義用', '乃是義用'),
    ('以埃後賢', '以俟後賢'),
    ('戒揚', '戒場'),
    ('如十三步勢分', '加十三步勢分'),
    ('至第人日', '至第八日'),
    ('增衣僧戒', '增衣價戒'),
    ('擲石及處', '擲石所及處'),
    ('無根憎殘謗', '無根僧殘謗'),
    ('䟦難陀', '跋難陀'),
    ('捉乳捉䏶', '捉乳捉髀'),
    ('護䏶、踝', '護髀、踝'),
    ('脚入䏶', '脚入髀'),
]
REPL_OUT = [
    ('終南大一山', '終南太一山'),
    ('乃是是義用', '乃是義用'),
    ('以埃後賢', '以俟後賢'),
    ('戒揚', '戒場'),
    ('如十三步', '加十三步'),
    ('至第人日', '至第八日'),
    ('增衣僧戒', '增衣價戒'),
    ('擲石及處', '擲石所及處'),
    ('憎殘', '僧殘'),
    ('䟦難陀', '跋難陀'),
    ('䏶', '髀'),
    ('𨤲', '釐'),
]


def apply(base, reps, label):
    total = {}
    for f in sorted(os.listdir(base)):
        if not f.endswith('.txt'):
            continue
        p = os.path.join(base, f)
        t = io.open(p, encoding='utf-8').read()
        b = t
        for a, c in reps:
            if a in t:
                n = t.count(a)
                t = t.replace(a, c)
                total[a] = total.get(a, 0) + n
        if t != b:
            io.open(p, 'w', encoding='utf-8').write(t)
    print(label, total)


if __name__ == '__main__':
    apply(S, REPL_SRC, 'SRC')
    apply(T, REPL_OUT, 'OUT')
