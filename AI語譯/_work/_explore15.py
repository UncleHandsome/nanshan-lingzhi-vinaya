import os,re
root=r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
for fn in ["02_四分律含注戒本疏.txt","03_四分律刪補隨機羯磨疏.txt","04_四分律比丘尼鈔.txt","05_四分律拾毗尼義鈔.txt"]:
    t=open(os.path.join(root,"TXT",fn),encoding="utf-8").read()
    print(fn, "記:",t.count("【記】"), "疏:",t.count("【疏】"), "chars",len(t))
# per 分卷_標點 file marker counts for 業疏
import glob
print("== 業疏 分卷 markers ==")
for f in sorted(glob.glob(os.path.join(root,"TXT_分卷_標點","03_業疏","*.txt")))[:6]:
    t=open(f,encoding="utf-8").read()
    print(os.path.basename(f), "記",t.count("【記】"),"疏",t.count("【疏】"),"lines",t.count(chr(10)))
