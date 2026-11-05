
# -*- coding: utf-8 -*-
import io, os
D = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
TR = [('《大智度論》等律論','《薩婆多論》'),('《僧祇論》說','《摩得勒伽論》說'),
      ('精通蛇毒的「行醫師」','精通咒治腹行蛇毒的「行胸師」'),
      ('止持作持終歸於','只歸結為（止歸）'),('思修壞正之「智」','思修懷正之「智」'),
      ('君子固窮□','君子固窮')]
SRC = [('弟子倫師衣','弟子偷師衣'),('減死從 𢷤','減死從流'),('無始結晴','無始結情'),
       ('若也物想','若他物想'),('長二文四尺','長二丈四尺'),('中問容草車','中間容草車'),
       ('佛陀 陀羅 䟦 譯','佛陀跋陀羅譯'),('婬唯適已','婬唯適己'),('令「引證」者','今「引證」者'),
       ('持云方重','持去方重')]
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
