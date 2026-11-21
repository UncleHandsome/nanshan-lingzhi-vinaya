# 對話材料 #0624

- event: assistant/message
- seq: 90819
- time: 1794888459587

---

Source has `\\n\\n` (two chars backslash backslash? repr shows `\\\\n` = actual `\\n` two chars: backslash backslash n? Confusing). It's over-escaped.

Simplest: change to use actual newline via chr(10) construction: `shuji_check=(chr(10)*2 + '**【鈔文】...')`. Patch that line fully.

Read line and replace with:
`            shuji_check=((chr(10) * 2 + '**【鈔文】須依比丘尼律制**：不得以比丘制硬套覆蓋。') if _note else ''),`

Do replace of the containing line by regex.