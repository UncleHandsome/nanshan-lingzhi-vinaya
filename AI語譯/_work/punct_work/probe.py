import json, os, re
base = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work"
src = r"C:\Users\lionc\OneDrive\桌面\XW\三大部\03_四分律刪補隨機羯磨疏_句讀_v3.txt"
v3 = open(src, encoding="utf-8").read()
inp = json.load(open(os.path.join(base, "ys_punct_in.json"), encoding="utf-8"))
# strip: keep chinese chars only for matching
PUNCT = set("，。、；：？！「」（）《》〈〉“”‘’—…·　 \n\r\t【】○●■□◎◇※～-")
def is_cjk(c):
    o = ord(c)
    return (0x3400 <= o <= 0x9FFF) or (0xF900 <= o <= 0xFAFF) or (0x20000 <= o <= 0x2FFFF) or (0xE000 <= o <= 0xF8FF) or c == "\u3007"
# build stripped v3 with index map
chars = []
idx = []
for i, c in enumerate(v3):
    if is_cjk(c) and c not in PUNCT:
        chars.append(c); idx.append(i)
sv3 = "".join(chars)
print("v3 cjk chars:", len(sv3))
# test match
tot = 0; hit = 0; partial = 0
for bi, (k, paras) in enumerate(inp.items()):
    for pi, p in enumerate(paras):
        s = "".join(c for c in p if is_cjk(c) and c not in PUNCT)
        tot += 1
        pos = sv3.find(s)
        if pos >= 0:
            hit += 1
        else:
            partial += 1
print("total", tot, "fullmatch", hit, "nomatch", partial)
