# -*- coding: utf-8 -*-
"""檢查五書長段是否切小段、是否對齊。"""
import io, json, os, re
B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BOOKS = {
 'xingshichao': ('行事鈔','TXT/01_四分律刪繁補闕行事鈔.txt'),
 'jieshu': ('戒疏','TXT/02_四分律含注戒本疏.txt'),
 'yeshu': ('業疏','TXT/03_四分律刪補隨機羯磨疏.txt'),
 'nicao': ('尼鈔','TXT/04_四分律比丘尼鈔.txt'),
 'yichao': ('義鈔','TXT/05_四分律拾毗尼義鈔.txt'),
}
def han(s): return ''.join(re.findall(r'[\u4e00-\u9fff]',str(s)))
print('book\tterm\tfinal\tlongrows\twhole>1000\texact')
for book,(name,rawp) in BOOKS.items():
    root=os.path.join(B,'測試','重譯',name,'_長段')
    def cnt(d):
        p=os.path.join(root,d)
        return len([f for f in os.listdir(p) if f.endswith(('.md','.txt'))]) if os.path.isdir(p) else 0
    term=cnt('_終審'); fin=cnt('_定稿')
    raw=io.open(os.path.join(B,rawp),encoding='utf-8').read(); h=han(raw)
    rows=[json.loads(x) for x in io.open(os.path.join(B,'定稿',book+'.jsonl'),encoding='utf-8') if x.strip()]
    longrows=[r for r in rows if '_L' in r.get('key','') or r.get('key','').startswith('L:')]
    whole=[r for r in longrows if r.get('raw_end',0)-r.get('raw_start',0)>1000]
    ex=sum(1 for r in longrows if r.get('raw_start',-1)>=0 and han(r.get('source',''))==h[r['raw_start']:r['raw_end']])
    print('%s\t%d\t%d\t%d\t%d\t%d'%(name,term,fin,len(longrows),len(whole),ex))
