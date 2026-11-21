# 對話材料 #0811

- event: assistant/message
- seq: 109097
- time: 1795053049932

---

Now test A1 and A2:

A1 norm: build test strings:
- '師長發現' → should remain 發現
- '助長發生' → remain
- '長久發展' → remain
- '總結發揮' → remain
- '果斷發心' → remain
- '剃髮' '落髮' '白髮' unchanged; '剃发' → 剃髮
- '長髮' unchanged (髮 already)
Run normalize? normalize does many things; simpler call the regex directly, but better test normalize output on short text. normalize may add 【鈔文】 etc.? It processes lines and labels. Use norm.normalize('師長發現\n助長發生\n長久發展\n總結發揮\n果斷發心\n剃发\n') and print.

Careful: normalize has _CC / SIMP conversions maybe. Print result.

A2 _looks_pasted needs src_unit >40 chars. Test:
- src = '一二三四五六七八九十一二三四五六七八九十一二三四五六七八九十' (40+)
- col3 = same string (verbatim, no particles) → should True now.
- col3 = same + '這是白話翻譯' with particles → True (prefix 18, ratio ~1.3 <1.5) → True.
- col3 = '「'+src+'」' + long translation (ratio >1.15?) → earlier guard returns False if >1.15.
Test meaningful cases.

Run tests.