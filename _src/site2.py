
# -*- coding: utf-8 -*-
import io, os, re, json, html

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
SITE = os.path.join(B, 'docs')

BOOKS = [
    dict(dir='01_行事鈔', out='xingshichao', title='四分律刪繁補闕行事鈔', by='唐·道宣律師　·　三大部之一'),
    dict(dir='02_戒疏', out='jieshu', title='四分律含注戒本疏', by='唐·道宣律師疏／宋·元照律師記　·　三大部之二'),
    dict(dir='03_業疏', out='yeshu', title='四分律刪補隨機羯磨疏', by='唐·道宣律師疏／宋·元照律師記　·　三大部之三', ju=True),
    dict(dir='資持記', srcdir='資持記_細分', out='zhichi', title='四分律行事鈔資持記', by='宋·元照律師　·　行事鈔之註'),
    dict(dir='04_比丘尼鈔', out='nicao', title='四分比丘尼鈔', by='唐·道宣律師　·　南山五大部之四', ju=True),
    dict(dir='05_拾毗尼義鈔', out='yichao', title='四分律拾毗尼義鈔', by='唐·道宣律師　·　南山五大部之五', ju=True),
]

def read_pairs(bookdir, srcdir=None, ju=False):
    if ju:
        import site_ju
        return [(v, [dict(o=o, t=t) for o, t in items]) for v, items in site_ju.get(bookdir)]
    S = os.path.join(B, 'TXT_分卷', srcdir or bookdir)
    T = os.path.join(B, 'AI語譯', 'out', bookdir)
    if not os.path.isdir(T): return []
    out = []
    for f in sorted(os.listdir(S)):
        if not f.endswith('.txt'): continue
        key = f[:-4]
        p = os.path.join(T, key + '.txt')
        if not os.path.exists(p): continue
        sp = [x.strip() for x in io.open(os.path.join(S, f), encoding='utf-8').read().split('\n')[5:] if x.strip()]
        tp = [x.strip() for x in re.split(r'\n\s*\n', io.open(p, encoding='utf-8').read()) if x.strip()]
        juan = key.split('_', 1)[1] if '_' in key else '全'
        n = min(len(sp), len(tp))
        out.append((juan, [dict(o=sp[i], t=tp[i]) for i in range(n)]))
    return out

def vol_key(j):
    if j.startswith('卷首'): return '__PRE__'
    m = re.match(r'卷[上中下]', j)
    if m: return m.group(0)
    m = re.match(r'卷[一二三四五六七八九十]+', j)
    return m.group(0) if m else j

FOOTER = ('<footer style="margin:3.5rem 0 0;padding-top:1.2rem;border-top:1px solid var(--line);'          'color:var(--fg2);font-size:12.5px;line-height:1.7">'
          '原文：CBETA 電子佛典（大正藏／卍續藏）。白話語譯：本站自製。'
          '兩者均採 <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hant" rel="license">CC BY-NC-SA 4.0</a> 授權：'
          '姓名標示－非商業性－相同方式分享。轉載請保留出處，且不得作商業使用。'
          '<br><a href="ROOTLICENSE">授權全文</a></footer>')

EXTRA_CSS = """
/* 目錄頁：書籍卡片 */
main .card{border:1px solid var(--line);border-radius:8px;padding:1.1rem 1.2rem;margin:1.2rem 0 1.6rem;background:#fff}
main .card h2{margin:0 0 .2rem;border:0;padding:0;font-size:1.2rem}
main .card .byline{margin:0 0 .9rem;color:var(--fg2);font-size:13px}
main .card .grp{display:flex;flex-wrap:wrap;gap:.5rem}
main .card .grp a{display:inline-block;padding:.32rem .8rem;border:1px solid var(--line);border-radius:999px;
  text-decoration:none;color:var(--accent);font-size:14px;background:#faf8f2}
main .card .grp a:hover{background:#efeade;border-color:var(--accent2)}
main .intro{color:var(--fg2);font-size:14px;margin:0 0 1.4rem}

nav details.navj>summary{display:block;padding:.32rem 1rem;cursor:pointer;color:var(--fg);font-size:13px;font-weight:600}
nav details.navj>summary::-webkit-details-marker{display:none}
nav details.navj>summary:before{content:"▸ ";color:var(--accent2);font-size:10px}
nav details.navj[open]>summary:before{content:"▾ "}
nav a.book{padding-left:1rem;font-weight:600;color:var(--fg);font-size:13.5px}
nav .bklist .bk{margin:.15rem 0 .45rem}
nav .bklist details.navj{margin:.1rem 0}
nav .bklist details.navj>summary{display:block;padding:.34rem 1rem .18rem;cursor:pointer;color:var(--fg);font-size:13px;font-weight:600;line-height:1.45;list-style:none}
nav .bklist details.navj>summary::-webkit-details-marker{display:none}
nav .bklist details.navj>summary:before{content:"▸ ";color:var(--accent2);font-size:10px}
nav .bklist details.navj[open]>summary:before{content:"▾ "}
nav .bklist details.navj>summary.cur{color:var(--accent)}
nav .bklist details.navj ul{list-style:none;margin:0;padding:0 1rem .25rem 1.75rem}
nav .bklist details.navj li a{display:block;padding:.12rem 0;color:var(--fg2);font-size:13px;line-height:1.5;text-decoration:none}
nav .bklist details.navj li a:hover{color:var(--accent);text-decoration:underline}
nav .bklist details.navj li a.cur{color:var(--accent);font-weight:600}
nav .toclist a{display:block;padding:.12rem 1rem;color:var(--fg2);font-size:13px;line-height:1.5;text-decoration:none}
nav .toclist a:hover{color:var(--accent);text-decoration:underline}
main h1{margin-bottom:.4rem}
.byline{color:var(--fg2);font-size:13px;margin:0 0 1.4rem}
.pair{margin:1.15rem 0;padding-bottom:.9rem;border-bottom:1px dotted var(--line)}
.pair .o{background:#f4efe2;border-left:3px solid #cdbc9c;padding:.45rem .8rem;color:#5d4c3a;
  font-size:15.5px;line-height:1.75;border-radius:0 4px 4px 0}
.pair .t{margin:.45rem 0 0;font-size:17px;line-height:1.95;text-align:justify}
.pager{display:flex;justify-content:space-between;margin:2.5rem 0 0;font-size:14px}
mark{background:#ffe9a8;padding:0 .08em;border-radius:2px}
#hits .hit{border-bottom:1px solid var(--line);padding:.8rem 0}
#hits .meta{color:var(--fg2);font-size:12.5px;margin-bottom:.2rem}
#hits .o{color:#5d4c3a;font-size:14px}
#hits .t{font-size:15.5px}
@media(max-width:820px){nav{display:none}main{padding:1.4rem}}
"""

SEC_RE = re.compile(r'^[○◎◯【]?\s*[\u4e00-\u9fff]{2,10}篇第[一二三四五六七八九十]+[】]?$')


VOL_ORDER = ['卷上之一', '卷上之二', '卷上之三', '卷上之四',
             '卷中之一', '卷中之二', '卷中之三', '卷中之四',
             '卷下之一', '卷下之二', '卷下之三', '卷下之四',
             '卷上', '卷中', '卷下', '卷一', '卷二', '卷三', '卷四',
             '上一上', '上一下', '上二', '上三', '上四',
             '中一上', '中一下', '中二', '中三上', '中三下', '中四上', '中四下',
             '下一', '下二', '下三', '下四']


def vol_order_key(v):
    try:
        return VOL_ORDER.index(v)
    except ValueError:
        return 999


def nav_html(cur_book=None, prefix='', toc=None, prev=None, nxt=None):
    parts = ['<nav><h1><a href="INDEX">南山律典・白話對照</a></h1>']
    parts.append('<div class="grp"><b>全書</b><a href="INDEX">目錄</a><a href="SEARCH">全文搜尋</a>'
                 '<a href="APPENDIX">附錄</a></div>')
    if (prev or nxt) and cur_book:
        parts.append('<div class="grp"><b>分卷</b>')
        if prev:
            parts.append('<a href="' + prefix + cur_book['out'] + '/' + prev + '.html">← ' + html.escape(prev) + '</a>')
        if nxt:
            parts.append('<a href="' + prefix + cur_book['out'] + '/' + nxt + '.html">' + html.escape(nxt) + ' →</a>')
        parts.append('</div>')
    if toc:
        parts.append('<div class="grp"><b>本卷篇目</b><div class="toch">')
        for sid, name in toc:
            parts.append('<a href="#p' + str(sid) + '">' + html.escape(name) + '</a>')
        parts.append('</div></div>')
    parts.append('<div class="grp"><b>書目</b><div class="bkh">')
    for bk in BOOKS:
        vols = bk.get('_vols') or []
        if not vols:
            continue
        here = cur_book and bk['out'] == cur_book['out']
        parts.append('<div class="bk"><span class="bkname">' + html.escape(bk['title']) + '</span><span class="vols">')
        for v, url in vols:
            mark = ' class="cur"' if here and cur_book and v == cur_book.get('_curvol') else ''
            parts.append('<a href="' + prefix + bk['out'] + '/' + v + '.html"' + mark + '>' + html.escape(v) + '</a>')
        parts.append('</span></div>')
    HB = ['卷上之一', '卷上之二', '卷上之三', '卷上之四', '卷中之一', '卷中之二', '卷中之三', '卷中之四',
          '卷下之一', '卷下之二', '卷下之三', '卷下之四']
    herehb = bool(cur_book and cur_book['out'] == 'hebian')
    parts.append('<div class="bk"><span class="bkname">行事鈔資持記・句級合編</span><span class="vols">')
    for v in HB:
        mark = ' class="cur"' if herehb and cur_book.get('_curvol') == v else ''
        parts.append('<a href="' + prefix + 'hebian/' + v + '.html"' + mark + '>' + html.escape(v) + '</a>')
    parts.append('</span></div></div></div></nav>')
    return ''.join(parts)


def page(title, body, cur_book=None, prefix='', toc=None, prev=None, nxt=None):
    nav = (nav_html(cur_book, prefix, toc, prev, nxt)
           .replace('INDEX', prefix + 'index.html')
           .replace('SEARCH', prefix + 'search.html')
           .replace('APPENDIX', prefix + 'appendix.html'))
    css = prefix + 'style.css?v=6'
    return ('<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>' + html.escape(title) + '｜南山律典・白話對照</title>'
            '<meta name="DC.rights" content="CC BY-NC-SA 4.0">'
            '<meta name="citation_author" content="UncleHandsome">'
            '<link rel="license" href="https://creativecommons.org/licenses/by-nc-sa/4.0/">'
            '<link rel="stylesheet" href="' + css + '"></head><body><div class="wrap">'
            + nav + '<main>' + body + FOOTER.replace('ROOT', prefix) + '</main></div></body></html>')

def build():
    os.makedirs(SITE, exist_ok=True)
    css_path = os.path.join(SITE, 'style.css')
    base_css = io.open(css_path, encoding='utf-8').read() if os.path.exists(css_path) else ''
    if 'details.navj>summary.cur' not in base_css:
        io.open(css_path, 'w', encoding='utf-8').write(base_css + '\n' + EXTRA_CSS)
    all_books = []
    for bk in BOOKS:
        pairs = read_pairs(bk['dir'], bk.get('srcdir'), bk.get('ju'))
        if not pairs: continue
        groups = {}
        for j, items in pairs:
            groups.setdefault(vol_key(j), []).extend(items)
        if '__PRE__' in groups:
            pre = groups.pop('__PRE__')
            first = list(groups.keys())[0] if groups else '卷一'
            groups[first] = pre + groups.get(first, [])
        bk['_vols'] = [(v, '') for v in sorted(groups, key=vol_order_key)]
        bk['_groups'] = groups
        all_books.append(bk)
    search_idx = {}
    for bk in all_books:
        outdir = os.path.join(SITE, bk['out']); os.makedirs(outdir, exist_ok=True)
        vols = list(bk['_groups'].keys())
        entries = []
        for i, v in enumerate(vols):
            items = bk['_groups'][v]
            body = ['<h1>' + html.escape(bk['title']) + '　' + html.escape(v) + '</h1>',
                    '<p class="byline">' + html.escape(bk['by']) + '　｜　白話對照</p>']
            toc = []
            for it in items:
                o = it['o'].strip()
                anchor = ''
                if SEC_RE.match(o):
                    sid = len(toc) + 1
                    toc.append((sid, o))
                    anchor = ' id="p' + str(sid) + '"'
                body.append('<div class="pair"' + anchor + '><div class="o">' + html.escape(it['o']) + '</div>'
                            + '<div class="t">' + html.escape(it['t']) + '</div></div>')
            prev = vols[i-1] if i > 0 else None
            nxt = vols[i+1] if i+1 < len(vols) else None
            bk['_curvol'] = v
            pager = ['<div class="pager">']
            pager.append('<a href="' + (prev + '.html') + '">← ' + html.escape(prev) + '</a>' if prev else '<span></span>')
            pager.append('<a href="' + (nxt + '.html') + '">' + html.escape(nxt) + ' →</a>' if nxt else '<span></span>')
            pager.append('</div>')
            body += pager
            io.open(os.path.join(outdir, v + '.html'), 'w', encoding='utf-8').write(
                page(bk['title'] + '　' + v, ''.join(body), bk, '../', toc, prev, nxt))
            for it in items:
                entries.append(dict(v=v, o=it['o'], t=it['t']))
        search_idx[bk['out']] = dict(title=bk['title'], entries=entries)
    # 搜尋索引（每本一檔）
    os.makedirs(os.path.join(SITE, 'search'), exist_ok=True)
    for out, data in search_idx.items():
        io.open(os.path.join(SITE, 'search', out + '.js'), 'w', encoding='utf-8').write('window.SIDX=window.SIDX||{};window.SIDX["' + out + '"]=' + json.dumps(data, ensure_ascii=False) + ';')
    # 目錄
    cards = []
    for bk in all_books:
        links = ''.join('<a href="' + bk['out'] + '/' + v + '.html">' + html.escape(v) + '</a>' for v in bk['_groups'])
        cards.append('<section class="card"><h2>' + html.escape(bk['title']) + '</h2>'
                     + '<p class="byline">' + html.escape(bk['by']) + '　·　' + str(len(bk['_groups'])) + ' 卷</p>'
                     + '<div class="grp">' + links + '</div></section>')
    idx_body = ('<h1>南山律典・白話對照</h1>'
                '<section class="card"><h2>行事鈔資持記・句級合編</h2><p class="byline">鈔文與記文逐段並列　·　12 卷</p><div class="grp"><a href="hebian/卷上之一.html">卷上之一</a><a href="hebian/卷上之二.html">卷上之二</a><a href="hebian/卷上之三.html">卷上之三</a><a href="hebian/卷上之四.html">卷上之四</a><a href="hebian/卷中之一.html">卷中之一</a><a href="hebian/卷中之二.html">卷中之二</a><a href="hebian/卷中之三.html">卷中之三</a><a href="hebian/卷中之四.html">卷中之四</a><a href="hebian/卷下之一.html">卷下之一</a><a href="hebian/卷下之二.html">卷下之二</a><a href="hebian/卷下之三.html">卷下之三</a><a href="hebian/卷下之四.html">卷下之四</a></div></section>' + '<p class="intro">道宣律師三大部與相關鈔疏的白話對照本，逐段原文與白話並列；原文採 CBETA 電子佛典（大正藏／卍續藏）。</p>' + '<p class="intro"><a href="appendix.html">附錄：名相與度量衡</a></p>'
                + ''.join(cards) + '<p class="byline"><a href="search.html">→ 全文搜尋</a></p>')
    io.open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8').write(page('目錄', idx_body))
    # 搜尋頁
    sb = ('<h1>全文搜尋</h1><input id="q" type="search" placeholder="輸入關鍵字，例如：羯磨、波羅夷、安居" '
          'style="width:100%;padding:.6rem .8rem;font-size:16px;border:1px solid var(--line);border-radius:6px;background:#fff">'
          '<p class="byline" id="count"></p><div id="hits"></div>'
          '<script>' + SEARCH_JS + '</script>')
    io.open(os.path.join(SITE, 'search.html'), 'w', encoding='utf-8').write(page('搜尋', sb))
    print('books', len(all_books), 'vols', sum(len(b['_groups']) for b in all_books))

SEARCH_JS = """
var BOOKS=[['xingshichao','四分律刪繁補闕行事鈔'],['yeshu','四分律刪補隨機羯磨疏'],['jieshu','四分律含注戒本疏'],['zhichi','四分律行事鈔資持記'],['nicao','四分比丘尼鈔'],['yichao','四分律拾毗尼義鈔'],['hebian','行事鈔資持記・句級合編']];
var loaded={};
function loadBook(id){ if(loaded[id]) return Promise.resolve(loaded[id]);
  return new Promise(function(res){ var s=document.createElement('script'); s.src='search/'+id+'.js';
    s.onload=function(){ loaded[id]=window.SIDX[id]; res(loaded[id]); }; s.onerror=function(){ res({entries:[]}); }; document.head.appendChild(s); }); }
function esc(s){return s.replace(/[&<>]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c];});}
function hl(s,q){return esc(s).split(esc(q)).join('<mark>'+esc(q)+'</mark>');}
async function run(q){
  var c=document.getElementById('count'), h=document.getElementById('hits');
  if(!q){ c.textContent=''; h.innerHTML=''; return; }
  c.textContent='搜尋中…';
  var out=[];
  for(var i=0;i<BOOKS.length;i++){
    var b=await loadBook(BOOKS[i][0]);
    var es=(b&&b.entries)||[];
    for(var j=0;j<es.length;j++){
      var e=es[j];
      if(e.o.indexOf(q)>=0||e.t.indexOf(q)>=0){ out.push({book:BOOKS[i][1],v:e.v,o:e.o,t:e.t,id:BOOKS[i][0]}); if(out.length>200) break; }
    }
    if(out.length>200) break;
  }
  c.textContent = out.length? ('找到 '+out.length+' 筆') : '沒有結果';
  var parts=[];
  for(var k=0;k<out.length;k++){ var x=out[k];
    parts.push('<div class="hit"><div class="meta">'+x.book+'・'+x.v+'　<a href="'+x.id+'/'+x.v+'.html">前往</a></div>'
      +'<div class="o">'+hl(x.o,q)+'</div><div class="t">'+hl(x.t,q)+'</div></div>');
  }
  h.innerHTML=parts.join('');
}
document.addEventListener('DOMContentLoaded',function(){
  var inp=document.getElementById('q'); if(!inp) return; var t;
  inp.addEventListener('input',function(e){ clearTimeout(t); t=setTimeout(function(){run(e.target.value.trim());},250); });
});
"""

build()
