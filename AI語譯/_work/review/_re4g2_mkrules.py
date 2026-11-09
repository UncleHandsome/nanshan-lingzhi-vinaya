# -*- coding: utf-8 -*-
src = open(r'AI語譯/_work/review/_re4g2_build.py', encoding='utf-8').read()
i = src.index('MAN = {')
j = src.index('SKIP_APPLIED =')
body = src[i:j]
# convert MAN/B_FIX python literal blocks into a module
mod = '# -*- coding: utf-8 -*-\n' + body
open(r'AI語譯/_work/review/_re4g2_rules.py', 'w', encoding='utf-8').write(mod)
ns = {}
exec(mod, ns)
print(len(ns['MAN']), len(ns['B_FIX']))
