import io
p=r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review\說明_r2_02d.md"
t=io.open(p,encoding="utf-8").read()
t=t.replace("`_apply3log.txt`（294 筆 OK 紀錄）","`_apply3log.txt`（286 筆 OK 紀錄，另有 9 筆以人工補做）")
io.open(p,"w",encoding="utf-8",newline="").write(t)
print("ok")
