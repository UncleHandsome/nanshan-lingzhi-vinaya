import re
p="tmp_apply.py"
s=open(p,encoding="utf-8").read()
s=s.replace('     ("福報窮盡無盡", "福報無窮無盡")],','     ("福德果報窮盡無盡", "福德果報無窮無盡")],')
s=s.replace('36: [("依照僧團長幼次序受請的人', '36: [("）經中又說", "經中又說"),\n     ("依照僧團長幼次序受請的人')
open(p,"w",encoding="utf-8").write(s)
print("patched")
