import io,csv,sys
sys.stdout.reconfigure(encoding='utf-8')
p=r'C:\Users\lionc\OneDrive\桌面\XW\三大部\合編材料\篇18_四藥受淨.csv'
rows=list(csv.reader(io.open(p,encoding='utf-8-sig')))
print('rows',len(rows))
zs=[r for r in rows[1:] if r[0]=='記']
cs=[r for r in rows[1:] if r[0]=='鈔']
print('記',len(zs),'鈔',len(cs))
print([(r[1],r[4]) for r in zs[:40]])
print([(r[1],r[2][:12]) for r in cs[:8]])
