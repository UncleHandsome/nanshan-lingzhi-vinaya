# -*- coding: utf-8 -*-
import _z6_lib as L
p = L.para("11a_中四上", 6)
i = p.find("元照自注")
print(repr(p[i-5:i+40]))
p7 = L.para("11a_中四上", 7)
for key in ["奪破","諳","詎","漁網"]:
    j = p7.find(key)
    print(key, repr(p7[j-10:j+20]) if j>=0 else "NOTFOUND")
