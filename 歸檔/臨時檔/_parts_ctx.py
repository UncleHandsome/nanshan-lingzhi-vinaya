cur = [l.rstrip("\n") for l in open("AI語譯/out/資持記/04d_上三.txt",encoding="utf-8")]
out=[]
for i in range(80, 96):
    out.append(f"--- line {i+1} (len {len(cur[i])}) ---")
    out.append(cur[i])
open("_parts_ctx04d.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
