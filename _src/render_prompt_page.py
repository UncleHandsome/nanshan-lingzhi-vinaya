# -*- coding: utf-8 -*-
"""產生 docs/prompt.html：校閱提示詞（可複製、方便閱讀）。

提示詞來源：_src/review_prompt_public.md（公開版）。內部審閱用版本另存 _src/review_prompt_universal.md（含 JSONL）。
"""
import html
import io
import os

import site_assets as SA

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(B, 'docs')
PROMPT = os.path.join(B, '_src', 'review_prompt_public.md')

COPY_JS = '''<script>
(function () {
  var btn = document.getElementById('copyPrompt');
  var msg = document.getElementById('copyMsg');
  var pre = document.getElementById('promptText');
  if (!btn || !pre) return;
  function done(ok) {
    if (msg) { msg.textContent = ok ? '已複製到剪貼簿' : '複製失敗，請手動全選複製'; }
    setTimeout(function () { if (msg) msg.textContent = ''; }, 2200);
  }
  btn.addEventListener('click', function () {
    var text = pre.textContent;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { done(true); }, function () { fallback(); });
    } else { fallback(); }
    function fallback() {
      try {
        var ta = document.createElement('textarea');
        ta.value = text; ta.setAttribute('readonly', '');
        ta.style.position = 'fixed'; ta.style.opacity = '0';
        document.body.appendChild(ta); ta.select();
        var ok = document.execCommand('copy');
        document.body.removeChild(ta); done(ok);
      } catch (e) { done(false); }
    }
  });
})();
</script>'''


def build():
    text = io.open(PROMPT, encoding='utf-8').read().rstrip('\n') + '\n'
    body = [
        '<h1>校閱提示詞</h1>',
        '<p class="byline">公開版（2026-11-26）。可直接複製給他人或 AI 使用的完整提示詞；'
        '材枓格式為每段 <code>## 書名／代號</code>＋原文＋白話。</p>',
        '<div class="prompt-actions">'
        '<button class="copy-btn" id="copyPrompt" type="button">⧉ 複製提示詞</button>'
        '<span class="copy-msg" id="copyMsg" role="status" aria-live="polite"></span>'
        '</div>',
        '<pre class="prompt-box" id="promptText">' + html.escape(text) + '</pre>',
        '<p class="byline">使用方式：把提示詞連同材料（<code>## …</code> 段落）一起送出；'
        '回覆依提示詞的「輸出格式」三節輸出。</p>',
        COPY_JS,
    ]
    out = SA.page('校閱提示詞｜南山律典', '\n'.join(body), prefix='',
                  book_label='校閱提示詞', book_short='提示詞',
                  body_class='page-prompt',
                  description='南山律典白話校閱提示詞（現行版），可查看與複製。')
    io.open(os.path.join(DOCS, 'prompt.html'), 'w', encoding='utf-8', newline='\n').write(out)
    print('prompt.html')


if __name__ == '__main__':
    build()
