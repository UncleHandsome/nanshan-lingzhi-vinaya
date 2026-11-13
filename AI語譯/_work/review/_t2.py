import io,re
p=r"C:\Users\lionc\OneDrive\桌面\XW\三大部\batch_qwen\r7k\resp_895.txt"
t=io.open(p,encoding="utf-8").read()
print(repr(t[:80]))
paras=[x.strip() for x in re.split(r"\n\s*\n",t) if x.strip()]
print(len(paras))
print(repr(paras[1][:80]))
print(bool(re.search(r"(\d{4})-(\d{4})",paras[1])))
