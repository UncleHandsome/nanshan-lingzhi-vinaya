import json, sys, os, re
ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
OUT = os.path.join(ROOT, "AI語譯", "out", "04_比丘尼鈔")
REV = os.path.join(ROOT, "校閱_7K")
CHUNKS = {"03a_卷中之上": "03a_卷中之上", "03b_卷中之上": "03b_卷中之上"}

def load(name):
    p = os.path.join(OUT, name + ".txt")
    with open(p, encoding="utf-8", newline="") as f:
        raw = f.read()
    return p, raw.split("\n")

def ne_idx(lines):
    return [i for i, l in enumerate(lines) if l.strip()]

def show(name, idx):
    p, lines = load(name)
    ne = ne_idx(lines)
    i = ne[idx - 1]
    for j in range(max(0, i - 2), min(len(lines), i + 3)):
        print(f"L{j+1}: {lines[j]}")
    print("---")

def cmp_rev(n):
    """compare review file 譯文 with out paragraphs"""
    path = os.path.join(REV, f"校閱_{n}.txt")
    txt = open(path, encoding="utf-8").read()
    blocks = re.findall(r"【%d-(\d{4})】04_比丘尼鈔/(\S+?)#(\d+)\n【原文】(.*?)\n【譯文】(.*?)(?=\n\n|\Z)" % n, txt, re.S)
    print(f"file {n}: {len(blocks)} blocks")
    for no, chunk, idx, orig, trans in blocks:
        name = CHUNKS.get(chunk)
        if not name:
            print("  UNKNOWN CHUNK", chunk); continue
        p, lines = load(name)
        ne = ne_idx(lines)
        cur = lines[ne[int(idx) - 1]]
        ok = cur == trans.strip()
        print(f"  #{idx} {chunk} len_rev={len(trans.strip())} len_out={len(cur)} same={ok}")
        if not ok:
            # find first diff
            a, b = trans.strip(), cur
            k = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), min(len(a), len(b)))
            print("    rev:", a[max(0,k-20):k+40])
            print("    out:", b[max(0,k-20):k+40])

def apply(path):
    edits = json.load(open(path, encoding="utf-8"))
    by = {}
    for e in edits:
        by.setdefault(e["chunk"], []).append(e)
    for chunk, items in by.items():
        p, lines = load(chunk)
        ne = ne_idx(lines)
        for e in items:
            i = ne[e["idx"] - 1]
            cur = lines[i]
            g = e.get("guard", "")
            if g and not cur.startswith(g):
                print("GUARD FAIL", chunk, e["idx"], cur[:40]); sys.exit(1)
            if "new" in e:
                cur = e["new"]
            for pair in e.get("subs", []):
                old, new = pair
                cnt = cur.count(old)
                if cnt != 1:
                    print(f"SUB COUNT {cnt} chunk={chunk} idx={e['idx']} old={old[:30]}"); sys.exit(1)
                cur = cur.replace(old, new, 1)
            lines[i] = cur
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write("\n".join(lines))
        print("written", chunk, len(items))

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "show":
        show(sys.argv[2], int(sys.argv[3]))
    elif cmd == "cmp":
        for n in sys.argv[2:]:
            cmp_rev(int(n))
    elif cmd == "apply":
        apply(sys.argv[2])
