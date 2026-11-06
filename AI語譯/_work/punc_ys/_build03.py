# -*- coding: utf-8 -*-
import json, re

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
SRC = ROOT + r"\AI語譯\_work\punc_ys\03.json"
REF = ROOT + r"\AI語譯\_work\punc_ys\_ref03_v2.json"
OUT = ROOT + r"\AI語譯\_work\punc_ys\out_03.json"

ALLOWED = set("，。、；：？！「」")

items = json.load(open(SRC, encoding="utf-8"))["items"]
ref = json.load(open(REF, encoding="utf-8"))["texts"]

# targeted fixes: (item index, old, new) -- each applied exactly once
FIX = [
    (2, "問中欲顯列相重舉之意。答中十戒已說，故曰前言；今復述之，故云重舉。",
        "問中，欲顯列相重舉之意。答中，十戒已說，故曰「前言」；今復述之，故云「重舉」。"),
    (3, "故云戒學別論。", "故云「戒學別論」。"),
    (4, "女則易為緣壞，增位尊彼沙彌，犯則隨缺便補。",
        "女則易為緣壞，增位尊。彼沙彌犯，則隨缺便補。"),
    (5, "則學頓而制緩也若準他文", "則學頓而制緩也。若準他文"),
    (6, "除自手取食、授食與他」者", "「除自手取食、授食與他」者"),
    (7, "彼謂除自手取，即開自不受而食也；授食與他，開為他作能授人也。",
        "彼謂「除自手取」，即開自不受而食也；「授食與他」，開為他作能授人也。"),
    (7, "不受授尼對簡大尼受已可授，", "「不受授尼」對簡大尼受已可授，"),
    (9, "當字去呼，代也。", "「當」字去呼，代也。"),
    (11, "隨時謂隨寒熱單重換易。", "「隨時」，謂隨寒熱單重換易。"),
]

texts = list(ref)
for i, old, new in FIX:
    assert texts[i].count(old) == 1, (i, old, texts[i].count(old))
    texts[i] = texts[i].replace(old, new)

def strip_all(s):
    return "".join(ch for ch in s if ch not in ALLOWED)

result = []
for it, t in zip(items, texts):
    t = t.strip()
    src = it["text"].strip()
    # align: every char must be a source char in order, or allowed punctuation
    ci = 0
    ins = []
    for ch in t:
        if ci < len(src) and ch == src[ci]:
            ci += 1
        elif ch in ALLOWED:
            ins.append(ch)
        else:
            raise SystemExit("BAD CHAR %r in item line %s" % (ch, it["line"]))
    if ci != len(src):
        raise SystemExit("INCOMPLETE item line %s (%d/%d)" % (it["line"], ci, len(src)))
    if strip_all(t) != strip_all(src):
        raise SystemExit("STRIP MISMATCH line %s" % it["line"])
    if not t.endswith("。"):
        raise SystemExit("NO PERIOD line %s" % it["line"])
    result.append({"file": it["file"], "line": it["line"], "text": t})

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)
    f.write("\n")

print("wrote", len(result), "items")
for r in result:
    print(r["line"], r["text"])
