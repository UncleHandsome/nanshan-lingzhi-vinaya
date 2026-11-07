import io, os

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
p = os.path.join(B, '_src', 'site2.py')
s = io.open(p, encoding='utf-8').read()

NEW_SEARCH = '''SEARCH_JS = """
var BOOKS=[['xingshichao','四分律刪繁補闕行事鈔'],['yeshu','四分律刪補隨機羯磨疏'],['jieshu','四分律含注戒本疏'],['zhichi','四分律行事鈔資持記'],['nicao','四分比丘尼鈔'],['yichao','四分律拾毗尼義鈔'],['hebian','行事鈔資持記・句級合編']];
var loaded={}, ACTIVE=-1;
function loadBook(id){ if(loaded[id]) return Promise.resolve(loaded[id]);
  return new Promise(function(res){ var s=document.createElement('script'); s.src='search/'+id+'.js';
    s.onload=function(){ loaded[id]=window.SIDX[id]; res(loaded[id]); }; s.onerror=function(){ res({entries:[]}); }; document.head.appendChild(s); }); }
function esc(s){return String(s).replace(/[&<>]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c];});}
function escq(s){return s.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&');}
function hl(s,q){ if(!q) return esc(s); var re=new RegExp('('+escq(q)+')','gi');
  return esc(s).replace(re,'<mark>$1</mark>'); }
function snip(s,q,n){ if(!q) return esc(s.slice(0,n));
  var i=s.toLowerCase().indexOf(q.toLowerCase()); if(i<0) return esc(s.slice(0,n));
  var a=Math.max(0,i-30), b=Math.min(s.length,i+q.length+70);
  return (a>0?'…':'')+hl(s.slice(a,b),q)+(b<s.length?'…':''); }
function score(e,q){ var s=0; if(e.o.indexOf(q)===0) s+=6; if(e.o.indexOf(q)>=0) s+=3;
  if(e.t.indexOf(q)>=0) s+=2; if((e.v||'').indexOf(q)>=0) s+=4; return s; }
async function run(q){
  var c=document.getElementById('count'), h=document.getElementById('hits');
  if(!q){ c.textContent=''; h.innerHTML=''; return; }
  c.textContent='搜尋中…'; var t0=Date.now(); var out=[];
  for(var i=0;i<BOOKS.length;i++){
    var b=await loadBook(BOOKS[i][0]); var es=(b&&b.entries)||[];
    for(var j=0;j<es.length;j++){ var e=es[j];
      if(e.o.indexOf(q)>=0||e.t.indexOf(q)>=0){
        out.push({book:BOOKS[i][1],bid:BOOKS[i][0],v:e.v,o:e.o,t:e.t,i:e.i||'',sc:score(e,q)});
      }
    }
  }
  out.sort(function(a,b){ return b.sc-a.sc; });
  var total=out.length; out=out.slice(0,300);
  c.textContent = total? ('找到 '+total+' 筆'+(total>300?'（顯示前 300 筆）':'')+'　·　'+(Date.now()-t0)+' ms') : '沒有結果';
  if(!total){
    h.innerHTML='<div class="empty">查無「'+esc(q)+'」。可試：<a href="?q=羯磨">羯磨</a>、<a href="?q=波羅夷">波羅夷</a>、<a href="?q=安居">安居</a>，或較短的關鍵字。</div>';
    return;
  }
  var parts=[], lastBook='';
  for(var k=0;k<out.length;k++){ var x=out[k];
    if(x.book!==lastBook){ parts.push('<h3 class="hitbook">'+esc(x.book)+'</h3>'); lastBook=x.book; }
    parts.push('<div class="hit" data-idx="'+k+'"><div class="meta">'+esc(x.v)
      +'　<a href="'+x.bid+'/'+x.v+'.html'+(x.i?'#'+x.i:'')+'">前往 →</a></div>'
      +'<div class="o">'+snip(x.o,q,110)+'</div><div class="t">'+snip(x.t,q,110)+'</div></div>');
  }
  h.innerHTML=parts.join('');
  ACTIVE=-1;
}
function setActive(i){
  var hs=document.querySelectorAll('#hits .hit'); if(!hs.length) return;
  if(ACTIVE>=0&&hs[ACTIVE]) hs[ACTIVE].classList.remove('active');
  ACTIVE=(i+hs.length)%hs.length; hs[ACTIVE].classList.add('active');
  hs[ACTIVE].scrollIntoView({block:'nearest'});
}
document.addEventListener('DOMContentLoaded',function(){
  var inp=document.getElementById('q'); if(!inp) return; var t;
  var m=(location.search.match(/[?&]q=([^&]*)/)||[]); if(m[1]){ inp.value=decodeURIComponent(m[1].replace(/\\+/g,' ')); run(inp.value.trim()); }
  inp.addEventListener('input',function(e){ clearTimeout(t); t=setTimeout(function(){
    var q=e.target.value.trim();
    if(history.replaceState) history.replaceState(null,'', q?('?q='+encodeURIComponent(q)):'search.html');
    run(q); },200); });
  inp.addEventListener('keydown',function(e){
    if(e.key==='ArrowDown'){ e.preventDefault(); setActive(ACTIVE+1); }
    else if(e.key==='ArrowUp'){ e.preventDefault(); setActive(ACTIVE-1); }
    else if(e.key==='Enter'){ var a=document.querySelector('#hits .hit.active a'); if(a) location.href=a.href; }
    else if(e.key==='Escape'){ inp.value=''; run(''); }
  });
  document.addEventListener('keydown',function(e){
    if(e.target&&/input|textarea|select/i.test(e.target.tagName)) return;
    if(e.key==='/'){ e.preventDefault(); inp.focus(); }
  });
});
"""'''

a = s.find('SEARCH_JS = """')
b = s.find('"""', s.find('document.addEventListener(\'DOMContentLoaded\'', a)) + 3
assert a > 0 and b > a
s = s[:a] + NEW_SEARCH + s[b:]

# 搜尋頁 HTML 加強
old_sb = """    sb = ('<h1>全文搜尋</h1><input id="q" type="search" placeholder="輸入關鍵字，例如：羯磨、波羅夷、安居" '
          'style="width:100%;padding:.6rem .8rem;font-size:16px;border:1px solid var(--line);border-radius:6px;background:#fff">'
          '<p class="byline" id="count"></p><div id="hits"></div>'
          '<script>' + SEARCH_JS + '</script>')"""
new_sb = """    sb = ('<h1>全文搜尋</h1>'
          '<div class="searchbox"><input id="q" type="search" placeholder="輸入關鍵字，例如：羯磨、波羅夷、安居" autocomplete="off" autofocus>'
          '<kbd>/</kbd></div>'
          '<p class="byline">可用 ↑↓ 選擇結果、Enter 開啟；結果依原文起始、卷名、白話加權排序。</p>'
          '<p class="byline" id="count"></p><div id="hits"></div>'
          '<script>' + SEARCH_JS + '</script>')"""
assert old_sb in s
s = s.replace(old_sb, new_sb, 1)

s = s.replace("style.css?v=9", "style.css?v=10")
s = s.replace("nav.js?v=5", "nav.js?v=6")
io.open(p, 'w', encoding='utf-8').write(s)
print('site2 patched')
