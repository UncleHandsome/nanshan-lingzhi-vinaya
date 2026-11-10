import io
p = r"AI語譯/_work/review/_re0_build.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace('''    if kind == "apply":
        old, new = op[1], op[2]
        n = text.count(old)
        if n != 1:
            return None, "OLD count=%d for %r" % (n, old[:60])
        return text.replace(old, new), None''','''    if kind == "apply":
        old, new = op[1], op[2]
        n = text.count(old)
        if len(op) > 3:
            idx = op[3]
            if n <= idx:
                return None, "OLD count=%d idx=%d for %r" % (n, idx, old[:60])
            pos = -1
            for _ in range(idx + 1):
                pos = text.find(old, pos + 1)
            return text[:pos] + new + text[pos + len(old):], None
        if n != 1:
            return None, "OLD count=%d for %r" % (n, old[:60])
        return text.replace(old, new), None''')
s = s.replace('''    if gid in D:
        op = D[gid]''','''    dkey = gid + "|" + e["type"]
    if dkey in D:
        op = D[dkey]
    elif gid in D:
        op = D[gid]''')
s = s.replace('''    if gid in D:
        op = D[gid]
        if op[0] == "skip":''','''    if gid in D or dkey in D:
        op = D.get(dkey) or D[gid]
        if op[0] == "auto":
            pairs=[p for p in e["pairs"] if p[0] in ("將A改為B","A改為B","刪除")]
            cur=e["current"] or ""
            for p in pairs:
                if p[1] and p[1] in cur:
                    ops.setdefault(k, []).append((gid, ("apply", p[1], p[2])))
            continue
        if op[0] == "skip":''')
io.open(p, "w", encoding="utf-8").write(s)
print("ok")
