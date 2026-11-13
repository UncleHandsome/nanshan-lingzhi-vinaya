import io,re,sys
p=r"C:\Users\lionc\OneDrive\桌面\XW\三大部\batch_qwen\r7k\resp_895.txt"
t=io.open(p,encoding="utf-8").read()
i=t.find("895-0001")
print(repr(t[i-12:i+20]))
print(repr(t[t.find("##"):t.find("##")+30]))
