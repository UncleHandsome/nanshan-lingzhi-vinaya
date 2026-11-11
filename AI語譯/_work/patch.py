import io
p=r"AI語譯\_work\apply_edits.py"
s=open(p,encoding="utf-8").read()
bad='f["orig"].count("\\n"], (book, chunk)'
good='f["orig"].count("\\n"), (book, chunk)'
print("found bad:", s.count(bad))
s=s.replace(bad,good)
open(p,"w",encoding="utf-8",newline="").write(s)
import py_compile
py_compile.compile(p, doraise=True)
print("compiled OK")
