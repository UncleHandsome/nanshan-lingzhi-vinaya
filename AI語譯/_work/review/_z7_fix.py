# -*- coding: utf-8 -*-
import _z6_lib as L
E=[
 ("11c_中四上",3,"（他說：）學人須於事上放免十二枝條","學人須於事上放免十二枝條"),
 ("11a_中四上",23,"因為想要劃分出四種行持","因為想要劃分出四行（止持、作持、止犯、作犯）"),
]
for c,p,o,n in E:
    print(c,p,L.apply_edits(c,[{"para":p,"old":o,"new":n}],dry=False))
