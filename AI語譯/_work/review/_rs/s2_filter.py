# -*- coding: utf-8 -*-
"""Screen claim corpus: which claims point at defects matching the 4 criteria,
and whether the quoted old wording is still live in the current paragraph."""
import io, os, re, json, collections

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
HERE = os.path.join(ROOT, "AI語譯", "_work", "review", "_rs")
OUTD = os.path.join(ROOT, "AI語譯", "out", "02_戒疏")

claims = json.load(io.open(os.path.join(HERE, "claims.json"), encoding="utf-8"))

def paras(chunk):
    t = io.open(os.path.join(OUTD, chunk + ".txt"), encoding="utf-8", newline="").read()
    ps = t.split("\r\n\r\n")
    if ps and ps[-1].endswith("\r\n"):
        ps[-1] = ps[-1][:-2]
    return ps

PC = {}
def get_paras(chunk):
    if chunk not in PC:
        PC[chunk] = paras(chunk)
    return PC[chunk]

CAT = {
 "A": r"讀不通|不成句|語法|主詞|主語|懸空|接不上|破碎|缺謂語|缺賓語|語意不完整|不知所云|句子結構|斷句|讀起來|讀成|語病|句子不",
 "B": r"生造|不成詞|非中文|自造|無此詞|不成話|不是詞|硬湊|怪詞|食古|不通順|拗口",
 "C": r"現代|今義|當代|專義|法律用語|行政| bureaucracy|現代漢語|現代詞",
 "D": r"重複|贅|疊字|衍字|累贅|同義|重出|兩次|前後重|複說|疊床|冗",
}

res = []
for c in claims:
    if not c["segs"]: continue
    txt = c["text"]
    hits = [k for k, p in CAT.items() if re.search(p, txt)]
    if not hits: continue
    chunk = c["chunks"][0]
    ps = get_paras(chunk)
    seg = c["segs"][0]
    cur = ps[seg-1] if 0 < seg <= len(ps) else ""
    quotes = [q for q in re.findall(r"[「『]([^」』\n]{4,90})[」』]", txt)]
    live = [q for q in quotes if q in cur]
    res.append({"rid": c["rid"], "bi": c["bi"], "chunk": chunk, "seg": seg,
                "cats": "".join(sorted(hits)), "live": len(live), "nq": len(quotes),
                "text": txt, "cur": cur})

res.sort(key=lambda r: (r["chunk"], r["seg"], r["rid"]))
json.dump(res, io.open(os.path.join(HERE, "screen.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)

print("flagged", len(res), collections.Counter(r["cats"] for r in res).most_common())
print("live-quote flagged", sum(1 for r in res if r["live"]))
L = []
for r in res:
    L.append("%s r%d #%d SEG%d live=%d/%d cats=%s | %s" % (r["chunk"][:3], r["rid"], r["bi"], r["seg"], r["live"], r["nq"], r["cats"], r["text"][:200]))
io.open(os.path.join(HERE, "screen.txt"), "w", encoding="utf-8").write("\n".join(L))
print("wrote screen.txt", len(L))
