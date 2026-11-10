import re, io
p = r"AI語譯/_work/review/_re0_analyze.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace('(?:改為|修正為|改譯為|改作|改成|修正作)「([^」]+)」", s):', '(?:改為|修正為|修改為|改譯為|改作|改成|修正作|更正為)「([^」]+)」", s):')
s = s.replace('r"「([^」]+)」(?:改為|修正為|改譯為|改作)「([^」]+)」"', 'r"「([^」]+)」(?:改為|修正為|修改為|改譯為|改作|改成)「([^」]+)」"')
s = s.replace('m = re.search(r"(?:修正為|改為|改譯為)「([^」]+)」", s)', 'm = re.search(r"(?:修正為|修改為|改為|改譯為|更正為)「([^」]+)」", s)')
io.open(p, "w", encoding="utf-8").write(s)
print("patched")
