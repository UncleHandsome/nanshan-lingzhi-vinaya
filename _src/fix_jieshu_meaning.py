import os, io, re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
T = os.path.join(B, 'AI語譯', 'out', '02_戒疏')

FIX = {
    '10a_卷三上之一': [
        ('終南山大一山沙門釋道宣撰寫', '終南太一山沙門釋道宣撰寫'),
        ('「殺二」（即「殺草」之筆誤）就是破壞生類', '「殺草」就是破壞生類'),
        ('【記文】在第五緣中。第一條緣，正式說明兩種涵義。',
         '【記文】在第五大章「具緣成」之中。第一條緣，正式說明兩種涵義。'),
    ],
    '10b_卷三上之一': [
        ('必定徑直墮入地獄', '一概墮入地獄，毫無例外'),
        ('罪報絕無減輕或間隔的餘地，所以說「必定徑直」',
         '罪報絕無減輕或間隔的餘地，所以說「一向」（純一無雜、毫無例外）'),
    ],
    '11b_卷三上之二': [
        ('房室私處的親暱禮遇', '房室之內的私密行徑'),
        ('說粗鄙親暱的話語', '說麤惡淫穢的言語'),
        ('談說粗鄙惡劣的言語', '談說麤惡淫穢的言語'),
    ],
}

n = 0
for key, reps in FIX.items():
    p = os.path.join(T, key + '.txt')
    t = io.open(p, encoding='utf-8').read()
    b = t
    for a, c in reps:
        if a in t:
            t = t.replace(a, c)
            n += 1
    if t != b:
        io.open(p, 'w', encoding='utf-8').write(t)
        print('fixed', key)
print('replacements', n)
