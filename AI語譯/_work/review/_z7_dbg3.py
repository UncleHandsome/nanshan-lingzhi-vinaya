# -*- coding: utf-8 -*-
import _z6_lib as L
p = L.para("11a_中四上",6)
i = p.find("曾見")
print(repr(p[i-12:i+8]))
print([hex(ord(c)) for c in p[i-1:i+6]])
