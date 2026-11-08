# -*- coding: utf-8 -*-
"""Optional: relocated fixes for the 3 report rows whose chunk/seg labels
point one paragraph (or one chunk) away from the paragraph that holds the
quoted problem sentence.  Writes fix_err2_g3_extra.tsv (NOT the main output).

Verified targets:
  09-1237: buggy text is 03b_卷一下之一 seg 78 (report said seg 79)
  10-0189: buggy text is 04a_卷一下之二 seg 72 (report said 03c seg 48)
  10-0353: buggy text is 04b_卷一下之二 seg 55 (report said seg 56)
"""
import io, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "fix_err2_g3_extra.tsv")
CORPUS = os.path.abspath(os.path.join(BASE, "..", "..", "out", "02_戒疏"))

CASES = [
    ("03b_卷一下之一", 78,
     [("如今應當質問彼人：「如果犯了下篇諸罪，豈不是在聽聞上篇時便構成非法，這就違背了律文中『犯者不得聽戒』的規定」，這又如何通達？",
       "如今應當反問質難彼人：「難道犯了下篇各罪的人，就可以聽聞上篇了嗎？若可以聽，這便違背了律文中『凡有犯者皆不得聽戒』的規定」，這又如何解釋得通呢？")]),
    ("04a_卷一下之二", 72,
     [("但三種請懺法實質是一致的；對首或獨念形式雖異，但發露言詞完全不差",
       "但同屬宣告三遍的懺悔法（三悔是一）；對首或獨念形式雖異，但同屬宣告一遍的懺悔法毫無差池（一說不差）")]),
    ("04b_卷一下之二", 55,
     [("「非人、畜生」這兩個異境，正犯時原是偷蘭遮，因疑心所以皆為突吉羅",
       "「非人、畜生」這兩個異境，正犯時原分別是偷蘭遮與波逸提（蘭提），因懷疑之故所以都只結突吉羅")]),
]


def paras(chunk):
    t = io.open(os.path.join(CORPUS, chunk + ".txt"), encoding="utf-8").read().strip()
    return [p for p in re.split(r"\r?\n\s*\r?\n", t) if p.strip()]


def main():
    lines = []
    for chunk, seg, edits in CASES:
        ps = paras(chunk)
        cur = ps[seg - 1]
        t = cur
        for old, new in edits:
            c = t.count(old)
            if c != 1:
                raise SystemExit(f"{chunk} seg{seg}: expected 1, found {c}")
            t = t.replace(old, new)
        assert t != cur and "\t" not in t and "\n" not in t
        lines.append(f"02_戒疏\t{chunk}\t{seg}\t{t}")
        print(f"OK {chunk} seg{seg} len {len(cur)} -> {len(t)}")
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", OUT, len(lines))


if __name__ == "__main__":
    main()
