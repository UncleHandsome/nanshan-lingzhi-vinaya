# 對話材料 #0883

- event: assistant/message
- seq: 111890
- time: 1795064617960

---

Order correct (post line56, mother line60). My check looked for '後文背景' earlier occurrence in prompt line5? No prompt has 後文背景? JI_NOTE maybe no. IndexOf finds first '後文背景' maybe in prompt? Actually line 5 has JI_NOTE, no. The check `$post -ge 0 -and $pos -gt $post` should be true; but IndexOf uses string '所釋鈔文' and '後文背景'; maybe mother appears in prompt (JI_NOTE says 材料若附【所釋鈔文...) at line5! So pos found prompt occurrence. Fine—actual order correct.

Now pack pending edge fixture p3:
```
【疏文】
[1] 疏1
[2] 疏文二
【記文】記文二
[3] 記文三
```
Expected b1=疏1; b2=疏文二+記文二; b3=記文三. Run split; check.

Then revise fixture (no 初審簡核, evidence present).

Run both.