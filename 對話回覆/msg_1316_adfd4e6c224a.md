# 對話材料 #1316

- event: assistant/message
- seq: 136790
- time: 1795251804977

---

Pair 780 missing prefix; pair 783 is continuation `一行覆竟...`; should prepend `餘取異部。《十誦》十五人：` to 783? AI key 780 but indices shifted; pair 780 currently 記文, pair 783 is 疏文 list. The missing text likely before 783; prepend to pair 783 source/tr.

Do:
- Remove huge 767.
- Replace 778 with corrected source/tr.
- Prepend to pair 783: `【疏文】餘取異部。《十誦》十五人：` + existing translation.
- Fix 799/800/808 (`《伽論》`, `《僧祇》`) and 801 colon.
Need identify current indices after removing 767; easier process by source phrases, not indices:
1. Remove pair with source starting `【疏文】二十二隱沒者即入地...` length >1000 (huge) — exact starts `二十二隱沒者` no comma. Keep short.
2. Replace source pair starting `【疏文】[1] 若爾，與四羯磨人` with corrected.
3. Find pair source starting `【疏文】一行覆竟人`; prepend.
4. For sources starting `【疏文】伽論》`, `【記文】伽論》`, `【記文】僧祇》`, add `《`.
5. Source `【疏文】今約癡鈍...五焉` add `：`.

Implement via regex/reconstruct; careful labels.