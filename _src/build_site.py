
# -*- coding: utf-8 -*-
import io, os, re, json, html

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SITE = os.path.join(B, 'docs')

BOOKS = [
    dict(dir='01_行事鈔', out='xingshichao', title='四分律刪繁補闕行事鈔', by='唐·道宣律師'),
    dict(dir='03_業疏', out='yeshu', title='四分律刪補隨機羯磨疏', by='唐·道宣律師疏／宋·元照律師記'),
]

def read_pairs(bookdir):
    S = os.path.join(B, 'TXT_分卷', bookdir)
    T = os.path.join(B, 'AI語譯', 'out', bookdir)
    out = []
    for f in sorted(os.listdir(S)):
        if not f.endswith('.txt'): continue
        key = f[:-4]
        tp_path = os.path.join(T, key + '.txt')
        if not os.path.exists(tp_path): continue
        sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tp = [x.strip() for x in re.split(r'\n\s*\n', io.open(tp_path, encoding='utf-8').read()) if x.strip()]
        juan = key.split('_', 1)[1] if '_' in key else '全'
        n = min(len(sp), len(tp))
        out.append((juan, [dict(o=sp[i], t=tp[i]) for i in range(n)]))
    return out

def vol_key(j):
    if j.startswith('卷首'): return '卷一'
    m = re.match(r'卷[上中下]', j)
    if m: return m.group(0)
    m = re.match(r'卷[一二三四五六七八九十]+', j)
    return m.group(0) if m else j

CSS = """
:root{--bg:#faf7f0;--ink:#22201c;--src:#6b5b4a;--acc:#8a4a1f;--line:#e3dccd}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"Noto Serif TC","Songti TC",serif;line-height:1.9}
header{position:sticky;top:0;background:rgba(250,247,240,.96);border-bottom:1px solid var(--line);padding:.6rem 1rem;display:flex;gap:1rem;align-items:center;z-index:9}
header a{color:var(--acc);text-decoration:none}
header .sp{flex:1}
main{max-width:52rem;margin:0 auto;padding:1rem 1.2rem 4rem}
h1{font-size:1.5rem}
h2{font-size:1.15rem;border-left:4px solid var(--acc);padding-left:.6rem;margin:2rem 0 .8rem}
.pair{margin:1.1rem 0}
.src{background:#f4efe2;border-left:3px solid #cdbc9c;padding:.4rem .7rem;color:var(--src);font-size:.95rem;line-height:1.75}
.tr{margin:.35rem 0 0;font-size:1.06rem;text-align:justify}
mark{background:#ffe9a8;padding:0 .1em}
nav.toc a{display:block;padding:.25rem 0;border-bottom:1px dotted var(--line)}
input[type=search]{width:100%;padding:.5rem .7rem;font-size:1rem;border:1px solid var(--line);border-radius:6px;background:#fff}
#res .hit{border-bottom:1px solid var(--line);padding:.6rem 0}
.meta{color:#8a7a66;font-size:.85rem}
"""

JS = """
async function loadAll(){
  if(window.__ALL__) return window.__ALL__;
  const man = await (await fetch('manifest.json')).json();
  const arr = await Promise.all(man.map(async function(m){
    const d = await (await fetch(m.file)).json();
    return {book:m.book, juan:m.juan, items:d.items, url:m.url};
  }));
  window.__ALL__ = arr; return arr;
}
function esc(s){ return s.replace(/[&<>]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c]; }); }
function hl(s,q){ return esc(s).split(esc(q)).join('<mark>'+esc(q)+'</mark>'); }
function render(hits,q){
  const box=document.getElementById('res');
  document.getElementById('count').textContent = hits.length ? ('找到 '+hits.length+' 筆') : '沒有結果';
  const parts=[];
  for(const h of hits){
    parts.push('<div class="hit"><div class="meta">'+h.book+'・'+h.juan+'</div>'
      +'<div class="src">'+hl(h.o,q)+'</div>'
      +'<div class="tr">'+hl(h.t,q)+'</div>'
      +'<div class="meta"><a href="'+h.url+'">前往</a></div></div>');
  }
  box.innerHTML = parts.join('');
}
async function doSearch(q){
  const box = document.getElementById('res');
  if(!q){ box.innerHTML=''; document.getElementById('count').textContent=''; return; }
  box.innerHTML = '<p class="meta">搜尋中…</p>';
  const all = await loadAll();
  const hits = [];
  for(const b of all){
    for(const it of b.items){
      if(it.o.indexOf(q)>=0 || it.t.indexOf(q)>=0) hits.push({book:b.book,juan:b.juan,url:b.url,o:it.o,t:it.t});
      if(hits.length>300) break;
    }
    if(hits.length>300) break;
  }
  render(hits,q);
}
document.addEventListener('DOMContentLoaded',function(){
  const inp=document.getElementById('q');
  if(inp){ let t; inp.addEventListener('input',function(e){ clearTimeout(t); t=setTimeout(function(){doSearch(e.target.value.trim());},300); }); }
});
"""

def page(title, body, root=''):
    head = '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
    head += '<meta name="viewport" content="width=device-width,initial-scale=1">'
    head += '<title>' + html.escape(title) + '</title>'
    head += '<link rel="stylesheet" href="' + root + 'style.css"></head><body>'
    head += '<header><a href="' + root + 'index.html">南山律典・白話對照</a><span class="sp"></span><a href="' + root + 'search.html">搜尋</a></header><main>'
    return head + body + '</main><script src="' + root + 'app.js"></script></body></html>'

def build():
    os.makedirs(SITE, exist_ok=True)
    io.open(os.path.join(SITE,'style.css'),'w',encoding='utf-8').write(CSS)
    io.open(os.path.join(SITE,'app.js'),'w',encoding='utf-8').write(JS)
    manifest = []; cards = []
    for bk in BOOKS:
        pairs = read_pairs(bk['dir'])
        groups = {}
        for j, items in pairs:
            groups.setdefault(vol_key(j), []).extend(items)
        os.makedirs(os.path.join(SITE,'data',bk['out']), exist_ok=True)
        links = []
        for v, items in groups.items():
            fn = bk['out'] + '_' + v + '.json'
            io.open(os.path.join(SITE,'data',bk['out'],fn),'w',encoding='utf-8').write(json.dumps(dict(items=items), ensure_ascii=False))
            url = 'data/' + bk['out'] + '/' + v + '.html'
            body = ['<h1>' + html.escape(bk['title']) + '　' + html.escape(v) + '</h1>']
            for it in items:
                body.append('<div class="pair"><div class="src">' + html.escape(it['o']) + '</div><div class="tr">' + html.escape(it['t']) + '</div></div>')
            io.open(os.path.join(SITE, url),'w',encoding='utf-8').write(page(bk['title']+'　'+v, '\n'.join(body), '../'))
            manifest.append(dict(book=bk['title'], juan=v, file='data/'+bk['out']+'/'+fn, url=url))
            links.append('<a href="' + url + '">' + html.escape(v) + '（' + str(len(items)) + ' 段）</a>')
        cards.append('<h2>' + html.escape(bk['title']) + '</h2><p class="meta">' + html.escape(bk['by']) + '</p><nav class="toc">' + ''.join(links) + '</nav>')
    io.open(os.path.join(SITE,'manifest.json'),'w',encoding='utf-8').write(json.dumps(manifest, ensure_ascii=False))
    idx = '<h1>南山律典・白話對照</h1><p>道宣律師三大部與相關鈔疏的白話對照本。</p>' + ''.join(cards) + '<p><a href="search.html">全文搜尋 →</a></p>'
    io.open(os.path.join(SITE,'index.html'),'w',encoding='utf-8').write(page('南山律典・白話對照', idx))
    sb = '<h1>全文搜尋</h1><input id="q" type="search" placeholder="輸入關鍵字，例如：羯磨、波羅夷、安居"><p class="meta" id="count"></p><div id="res"></div>'
    io.open(os.path.join(SITE,'search.html'),'w',encoding='utf-8').write(page('搜尋', sb))
    print('pages', len(manifest), 'books', len(BOOKS))

build()
