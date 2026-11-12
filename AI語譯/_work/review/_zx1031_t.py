import os, sys, json
LOG = os.path.join("AI語譯", "_work", "review", "_zx1031_log")
noop = 0; total = 0; bad = []
for fn in sorted(os.listdir(LOG)):
    if not fn.startswith("log_"): continue
    n = int(fn[4:-5])
    if not (1031 <= n <= 1180): continue
    d = json.load(open(os.path.join(LOG, fn), encoding="utf-8"))
    for e in d["edits"]:
        total += 1
        if e["old"] == e["new"]:
            noop += 1; bad.append((n, e["chunk"], e["seg"]))
print("edits", total, "noop", noop, bad[:5])
