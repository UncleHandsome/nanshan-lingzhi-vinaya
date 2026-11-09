import ast, json, re

src = open("AI語譯/_work/review/_build.py", encoding="utf-8").read()
tree = ast.parse(src)
man = None
for node in tree.body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "MANUAL":
        man = ast.literal_eval(node.value)

jb = json.load(open("AI語譯/_work/review/_jb.json", encoding="utf-8"))
def norm(s):
    return s.replace("『", "「").replace("』", "」")

recs = []
for i, x in enumerate(jb):
    cur = x["current"]
    s = x["suggestion"].strip()
    if i in man:
        for old, new in man[i]:
            recs.append(dict(i=i, seg=x["seg"], chunk=x["chunk"], a=old, b=new, mode="manual"))
        continue
    if not s:
        continue
    pairs = re.findall(r"「([^」]{1,200})」\s*(?:改為|改成|改譯為|修訂為|應改為)\s*「([^」]{1,400})」", s)
    for a, b in pairs:
        b = re.sub(r"（或[^（）]*）", "", b)
        recs.append(dict(i=i, seg=x["seg"], chunk=x["chunk"], a=a, b=b, mode="mech"))

# seam check on final output
out = {}
for line in open("AI語譯/_work/review/fix_re5_g1.tsv", encoding="utf-8"):
    book, chunk, seg, new = line.rstrip("\n").split("\t")
    out[(chunk, seg)] = new

flags = []
for r in recs:
    t = out.get((r["chunk"], r["seg"]), "")
    nb = r["b"]
    pos = t.find(nb)
    used = nb
    if pos < 0:
        nb = norm(r["b"]); pos = t.find(nb); used = nb
    if pos < 0:
        flags.append((r["i"], r["seg"], "B-not-found"))
        continue
    pre = t[max(0, pos - 6):pos]
    suf = t[pos + len(nb):pos + len(nb) + 6]
    # duplicate seam
    for k in (3, 4):
        if len(pre) >= k and len(nb) >= k and pre[-k:] == nb[:k]:
            flags.append((r["i"], r["seg"], "dup-pre", pre[-k:] + "|" + nb[:k]))
        if len(suf) >= k and len(nb) >= k and suf[:k] == nb[-k:]:
            flags.append((r["i"], r["seg"], "dup-suf", nb[-k:] + "|" + suf[:k]))
    r["pre"] = pre
    r["suf"] = suf

print("recs", len(recs), "flags", len(flags))
for f in flags[:60]:
    print(f)

json.dump(recs, open("AI語譯/_work/review/_recs.json", "w", encoding="utf-8"), ensure_ascii=False)

# big replacements
big = [r for r in recs if len(r["b"]) - len(r["a"]) > 12 or len(r["a"]) - len(r["b"]) > 6]
print("big", len(big))
with open("AI語譯/_work/review/_big.txt", "w", encoding="utf-8") as f:
    for r in big:
        f.write("[%d] %s seg%s\n  A: %s\n  B: %s\n  CTX: ...%s【%s】%s...\n\n" % (
            r["i"], r["chunk"], r["seg"], r["a"], r["b"], r.get("pre",""), r["b"], r.get("suf","")))


