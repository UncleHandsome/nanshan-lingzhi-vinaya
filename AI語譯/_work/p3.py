import json,os,sys,collections
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\lionc\OneDrive\桌面\XW\三大部")
d=json.load(open(r"AI語譯\_work\parsed.json",encoding="utf-8"))
yes=[e for e in d if e["verdict"]=="是錯"]
keys=[e["key"] for e in yes]
print("是錯 total",len(yes),"unique",len(set(keys)))
for e in yes:
    print(f'{e["src"]:>11} | {e["key"]:<12} | tag={e["tag"]!r:<6} | sugLen={len(e["sug"] or "")} | judLen={len(e["judge"])}')
