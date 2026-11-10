import io
p = r"AI語譯/_work/review/_re0_decisions.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace('"古人說：「安居未結束而解界會破夏」，那也可以說「安居未結束而舉行自恣會破夏」",', '"古人說：「安居未結束而解界會破夏」，那也可以說「安居未結束而舉行自恣會破夏」。",')
s = s.replace('"古人主張「安居未結束而解界會破夏」，（若照此推論，）難道也可以說安居未結束而自恣便會破夏嗎？"),', '"古人主張「安居未結束而解界會破夏」，（若照此推論，）難道也可以說安居未結束而自恣便會破夏嗎？"),')
io.open(p, "w", encoding="utf-8").write(s)
print("ok")
