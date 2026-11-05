
# -*- coding: utf-8 -*-
import io, os
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
tr_reps = [
 ('依據本草《四分律》','依據本律《四分律》'),
 ('《僧祇律論》說','《摩得勒伽論》說'),
 ('《僧伽羅叉論》說','《摩得勒伽論》說'),
 ('犯提舍尼罪','犯波逸提罪（單墮）'),
 ('另外劃分了子界','另外形成了多個界域（若干界）'),
 ('許諾不給對方帶來任何惱害觸犯','使得彼此不產生任何惱害觸犯'),
 ('按照凡夫的情見','按照凡夫的情見'),
]
src_reps = [('殺二」即壞生','殺草」即壞生'),('阿關罪聚','何關罪聚'),('「磨羯」','「羯磨」'),
            ('擔、避、乞縷','擔、擗、乞縷'),('蠶綿、而黑、白毛','蠶綿、純黑、白毛'),
            ('[卯/貝]','貿'),('十毫為 ，𨤲 𨤲十 為分','十毫為釐，十釐為分'),('若子界','若干界')]
def run(sub, reps):
    base = os.path.join(D, sub, '02_戒疏') if sub=='TXT_分卷' else os.path.join(D,'AI語譯','out','02_戒疏')
    n=0
    for f in sorted(os.listdir(base)):
        if not f.endswith('.txt'): continue
        p=os.path.join(base,f); t=io.open(p,encoding='utf-8').read(); b=t
        for a,c in reps: t=t.replace(a,c)
        if t!=b: io.open(p,'w',encoding='utf-8').write(t); n+=1
    print(sub,'files',n)
run('TXT_分卷', src_reps)
run('AI語譯', tr_reps)
