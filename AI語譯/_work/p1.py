import re, glob, os, json, collections
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
pat = re.compile(r'【存疑\s*([^】]+)】\s*([^/\s]+)/([^#\s]+)#(\d+)')
maps = {}
dups = collections.defaultdict(list)
for f in sorted(glob.glob(r"存疑材料\complex_存疑\complex_*.md")):
    txt = open(f, encoding="utf-8").read()
    for m in pat.finditer(txt):
        key = m.group(1).strip()
        maps.setdefault(key, []).append((f, m.group(2), m.group(3), int(m.group(4))))
print("total 存疑 keys:", len(maps))
multi = {k:v for k,v in maps.items() if len(v)>1}
print("keys with >1 mapping:", len(multi))
for k,v in list(multi.items())[:10]:
    print(k, v)
json.dump({k:v[0] for k,v in maps.items()}, open(r"AI語譯\_work\keymap.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
