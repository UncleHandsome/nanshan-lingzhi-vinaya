
# -*- coding: utf-8 -*-
import io, os
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
TR = [('名詞出自《薩婆多毗尼毗婆沙》','名詞出自《律二十二明了論》'),
      ('道光律師','慧光律師'),('復活復活起立','復活重新站起'),('美好的美德','美善的名德'),
      ('通反示分','通達示分'),('過受樂戒','過受藥戒'),
      ('如轉輪聖王般的莊嚴高座','底座可轉向各方的轉輪高座'),
      ('十四億四千萬歲','十四億四萬歲'),('舌䑛食戒','舌舐食戒')]
SRC = [('三木行世','三本行世'),('自餘成不等相','自餘成否等相'),('如律犬疏','如律大疏'),
       ('舌 食䑛 戒','舌舐食戒'),('過受樂戒','過受藥戒'),('通反示分','通達示分'),
       ('佛陀 陀跋 羅','佛陀跋陀羅')]
def run(sub, reps):
    base = os.path.join(D, sub, '02_戒疏') if sub=='TXT_分卷' else os.path.join(D,'AI語譯','out','02_戒疏')
    n=0
    for f in sorted(os.listdir(base)):
        if not f.endswith('.txt'): continue
        p=os.path.join(base,f); t=io.open(p,encoding='utf-8').read(); b=t
        for a,c in reps: t=t.replace(a,c)
        if t!=b: io.open(p,'w',encoding='utf-8').write(t); n+=1
    print(sub,'files',n)
run('TXT_分卷', SRC)
run('AI語譯', TR)
