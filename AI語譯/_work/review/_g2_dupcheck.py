# -*- coding: utf-8 -*-
import json
rows = json.load(open(r"AI語譯/_work/review/_g2_re9_rows.json", encoding="utf-8"))
by = {d["_line"]: d for d in rows}

tests = {
 79: ["釋主客篇。久住在寺院的僧人稱為主", "猛然一讀語句的氣勢"],
 177: ["《十誦律》說：比丘用齋完畢", "第六「面對境界的持犯」", "第二「自己煮食」"],
 181: ["第一「藥物的體質」（藥體）", "第四是「盡形壽藥」"],
 182: ["首先「手受的意旨」", "其次「口受的意旨」"],
 183: ["首先「受持時食」", "第二「受持非時漿的口說作法」"],
 184: ["第三「受持七日藥的作法」", "若若是葡萄"],
 185: ["像這樣風病服油", "第四「受持盡形壽藥的作法」"],
 22: ["袒露胸腹行走"],
}
for ln, phrases in tests.items():
    d = by.get(ln)
    if not d:
        print(ln, "MISSING ROW")
        continue
    print("=" * 80)
    print("L%d %s %s s%s  len=%d" % (ln, d["book"], d["chunk"], d["seg"], len(d["current"])))
    for p in phrases:
        print("  count(%s) = %d" % (p[:20], d["current"].count(p)))
