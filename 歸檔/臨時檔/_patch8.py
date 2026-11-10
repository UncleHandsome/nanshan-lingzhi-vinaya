import io
p = r"AI語譯/_work/review/_re0_decisions.py"
s = io.open(p, encoding="utf-8").read()
old = '"053-0063": ("mis", "本段現行文字為安居受日、破夏之問答，建議卻要求改為「說戒住持」之文，二者主題全不相應，屬貼錯段。"),'
new = '"053-0063": ("rebuild", "【疏文】註解中引用《四分律》所說「隨各個住處必須具備說戒」這段文，是展現佛法得以住持的行相。"),'
assert old in s
s = s.replace(old, new)
io.open(p, "w", encoding="utf-8").write(s)
print("ok")
