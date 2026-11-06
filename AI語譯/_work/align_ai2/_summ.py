import json, glob, os
base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\align_ai2"
lines = []
for f in sorted(glob.glob(os.path.join(base, "0*.json"))):
    d = json.load(open(f, encoding="utf-8"))
    it = d["items"]; ca = d["cand"]
    lines.append(f"{os.path.basename(f)}: items={len(it)} z={it[0]['z']}..{it[-1]['z']} cand={len(ca)} c={ca[0]['c']}..{ca[-1]['c']} sec={d.get('sec')}")
lines.append("")
for f in ["out_002.json", "out_007.json"]:
    p = os.path.join(base, f)
    if os.path.exists(p):
        d = json.load(open(p, encoding="utf-8"))
        m = d["map"]
        lines.append(f"{f}: n={len(m)} z={m[0]['z']}..{m[-1]['z']} c={m[0]['c']}..{m[-1]['c']} minc={min(x['c'] for x in m)} maxc={max(x['c'] for x in m)} mono={all(m[i]['c']<=m[i+1]['c'] for i in range(len(m)-1))}")
open(os.path.join(base, "_summ.txt"), "w", encoding="utf-8").write("\n".join(lines))
print("ok")
