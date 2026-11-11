import os,re,glob,json
files=[]
for p in glob.glob('batch_qwen/r2/resp_*.txt'):
    n=int(re.search(r'(\d+)',os.path.basename(p)).group(1))
    if 1331<=n<=1648: files.append((n,p))
files.sort()
print('files',len(files))
stat={}
for n,p in files:
    s=open(p,encoding='utf-8-sig').read()
    sec=len(re.findall(r'^###\s*【',s,re.M))
    bi=s.count('必改'); wen=s.count('⚠️'); bi2=s.count('✏️'); ok=s.count('✔️')
    stat[n]=(sec,bi,wen,bi2,ok,len(s))
import statistics
print('avg len',sum(v[5] for v in stat.values())//len(stat))
print('avg 必改',sum(v[1] for v in stat.values())/len(stat))
print('avg sec',sum(v[0] for v in stat.values())/len(stat))
print('no 必改 files',sum(1 for v in stat.values() if v[1]==0))
print('sample', list(stat.items())[:5])
