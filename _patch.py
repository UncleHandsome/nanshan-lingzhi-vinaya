import re, io
p = r"AI語譯\_work\review\_re0_build_ctx.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace('    gid, loc, prio, typ = m.group(1), m.group(2), m.group(3), m.group(4)\n',
              '    gid, loc, prio, typ = m.group(1), m.group(2).lstrip("｜|"), m.group(3), m.group(4)\n')
io.open(p, "w", encoding="utf-8").write(s)
