# -*- coding: utf-8 -*-
import io, re
for ch, seg in [("16b_下四", 1), ("16c_下四", 1), ("16d_下四", 1), ("16a_下四", 1)]:
    p = "AI語譯/out/資持記/%s.txt" % ch
    try:
        t = io.open(p, encoding="utf-8").read()
    except Exception as e:
        print(ch, "ERR", e); continue
    paras = [x for x in re.split(r"\r?\n\r?\n", t) if x.strip()]
    print("=" * 80)
    print(ch, "n", len(paras))
    print(repr(paras[seg - 1][:200]))
