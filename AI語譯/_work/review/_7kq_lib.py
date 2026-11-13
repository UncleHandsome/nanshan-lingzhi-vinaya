# -*- coding: utf-8 -*-
"""7K 卷二下之二 校閱輔助：讀材料、譯文、原文、記文。"""
import os, re, io, json, sys

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
BOOK = "02_戒疏"

def rd(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()

def wr(p, s):
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)

SEG_RE = re.compile(r"^【(\d{3})-(\d{4})】(\S+)#(\d+)\s*$")

def load_material(n):
    """return list of dict(idx,label,bookchunk,para,orig,origkind,trans)"""
    t = rd(os.path.join(ROOT, "校閱_7K", f"校閱_{n}.txt"))
    lines = t.split("\n")
    segs = []
    cur = None
    buf = {"原文": [], "譯文": []}
    def flush():
        if cur is not None:
            cur["orig"] = "\n".join(buf["原文"]).strip()
            cur["trans"] = "\n".join(buf["譯文"]).strip()
            segs.append(cur)
    for ln in lines:
        m = SEG_RE.match(ln.strip())
        if m:
            flush()
            bc = m.group(3).split("/")[-1]
            cur = {"idx": m.group(1), "seg": m.group(2), "bookchunk": bc,
                   "para": int(m.group(4))}
            buf = {"原文": [], "譯文": []}
            continue
        if cur is None:
            continue
        s = ln.strip()
        if s.startswith("【原文】"):
            buf["原文"].append(s[len("【原文】"):])
        elif s.startswith("【譯文】"):
            buf["譯文"].append(s[len("【譯文】"):])
        elif s and buf["原文"] and not buf["譯文"]:
            # 續行原文
            buf["原文"].append(s)
        elif s:
            buf["譯文"].append(s)
    flush()
    return segs

def out_path(bookchunk):
    return os.path.join(ROOT, "AI語譯", "out", BOOK, bookchunk + ".txt")

def para_sep(t):
    return "\r\n\r\n" if "\r\n" in t else "\n\n"

def load_paras(bookchunk):
    t = rd(out_path(bookchunk))
    return t.split(para_sep(t))

def para_of(bookchunk, n):
    return load_paras(bookchunk)[n-1]

def src_path(bookchunk):
    return os.path.join(ROOT, "TXT_分卷", BOOK, bookchunk + ".txt")

def load_src(bookchunk):
    return rd(src_path(bookchunk))

def resp(n):
    p = os.path.join(ROOT, "batch_qwen", "r7k", f"resp_{n}.txt")
    if os.path.exists(p):
        return rd(p), "r7k"
    p2 = os.path.join(ROOT, "待跑_審查擋掉7K", "回覆", f"檔{n}.txt")
    if os.path.exists(p2):
        return rd(p2), "待跑"
    return None, None

if __name__ == "__main__":
    n = sys.argv[1] if len(sys.argv) > 1 else "592"
    segs = load_material(n)
    print("材料段數", len(segs))
    for s in segs[:3]:
        print(s["seg"], s["bookchunk"], s["para"])
        print("  原:", s["orig"][:60])
        print("  譯:", s["trans"][:60])
    bc = segs[0]["bookchunk"]
    paras = load_paras(bc)
    print("譯文段落數", len(paras), "檔案", bc)
    p = segs[0]["para"]
    print(f"段落#{p} 前60:", paras[p-1][:80])
    print("與材料譯文相符:", paras[p-1].strip() == segs[0]["trans"].strip())
