import io
p = r"AI語譯/_work/review/_re0_decisions.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace('"011-0006": ("apply",', '"011-0006|意思相反": ("apply",')
s = s.replace('"040-0011": ("apply",\n  "應當指給他們看房舍、床座等佛物，指點佛塔旁的供具等",', '"040-0011": ("apply",\n  "應當指給他們看房舍、床座等佛物，或指點佛塔旁的供具等",')
s = s.replace('卻因為「將活人誤想為非人」的緣故，所以只判定微輕的心念罪（方便罪）。有時面對非獲罪的對象，或因「將有主之物誤想為無主之物」的緣故', '卻因為『將活人誤想為非人』的緣故，所以只判定微輕的心念罪（方便罪）。有時面對非獲罪的對象，或因『將有主之物誤想為無主之物』的緣故')
# add missing entries at end
add = '''
D["011-0006|術語錯"] = ("auto",)
D["065-0046"] = ("apply", "相當於此地的九月二十四日", "相當於此地的九月十日", 0)
'''
s = s + add
io.open(p, "w", encoding="utf-8").write(s)
print("patched")
