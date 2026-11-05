
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
