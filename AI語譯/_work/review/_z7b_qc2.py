import sys
sys.path.insert(0,'.')
import _z6_lib as L
for c in ["10c_中三下","10d_中三下","11a_中四上"]:
    t,s = L.paras(c)
    print(c, "paras", len(t.split(s)), "lines", t.count("\n"))
