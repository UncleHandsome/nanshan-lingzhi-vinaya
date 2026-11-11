p=r"AI語譯\_work\edits.py"
s=open(p,encoding="utf-8").read()
bad='''("01_行事鈔","09d_卷下之一",1,
  "師父亡故之後，全部歸入常住僧物。","師父亡故之後，全部歸入僧團。",'''
good='''("01_行事鈔","09c_卷下之一",1,
  "師父亡故之後，全部歸入常住僧物。","師父亡故之後，全部歸入僧團。",'''
print("found:", s.count(bad))
open(p,"w",encoding="utf-8",newline="").write(s.replace(bad,good))
