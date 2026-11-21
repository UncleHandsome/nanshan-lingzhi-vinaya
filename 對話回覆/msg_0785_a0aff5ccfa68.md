# 對話材料 #0785

- event: assistant/message
- seq: 107505
- time: 1795047534831

---

Good — importers insert `_src` into sys.path. So top-level `import book_config as BC` is safe (book_config only imports os).

Now the patch. I'll rewrite lines 47-112 (BASE_PROMPT, get_prompt, prompt_for) carefully.

Design of unified code:

```python
BASE_PROMPT = ( ... unchanged ... )

# 一審三分支（疏＋記、單疏、單記）共用同一套文注脈絡與疏記互核規範
_SH_CTX, _SH_PAIR = __import__('book_config').SHUJI_CTX
```

Better explicit import at top: `import book_config as BC`? The file currently uses `__import__('book_config')` inside get_prompt and `from book_config import ...` inside prompt_for — historical leftovers from refactors. Adding a clean top import `import book_config as BC` and using BC.CFG etc. reduces the `__import__` weirdness. But minimal diff is safer. However "統一" is about content, not imports. Still, a top-level import is cleaner and I can verify compile.

Let me write:

```python
import book_config as BC
```
right after `import io`? Order: argparse, io, json, os, materials_io as MI, re. Insert `import book_config as BC` after `import argparse`? Alphabetical-ish not enforced. I'll put after `import os` line... Actually `import materials_io as MI` then `import re`. I'll add `import book_config as BC` before materials_io to keep local imports together:

```
import argparse
import io
import json
import os
import re

import book_config as BC
import materials_io as MI
```

Hmm, moving `re` up changes order slightly; fine but minimal diff: just add one line `import book_config as BC` after `import os` and leave the rest.

Then:

```python
SHUJI_CTX = BC.SHUJI_CTX
SHUJI_BASE, SHUJI_PAIR = SHUJI_CTX
```

Hmm naming collision with imported? No.

get_prompt:

```python
def get_prompt(is_nicao=False):
    if is_nicao:
        _note = (BC.CFG.get('尼鈔') or {}).get('note', '')
        return BASE_PROMPT.format(
            scope='鈔文',
            split_target='【鈔文】',
            book_ctx=_note,
            shuji_check=((chr(10) * 2 + '**【鈔文】須依比丘尼律制**：不得以比丘制硬套覆蓋。') if _note else ''),
            style_spec=BC.STYLE_SPEC,
            logic_checklist=BC.LOGIC_CHECKLIST,
            out_format='     【鈔文】……',
        )
    return BASE_PROMPT.format(
        scope='疏文與記文',
        split_target='【疏文】與【記文】',
        book_ctx=SHUJI_BASE,
        shuji_check=SHUJI_PAIR,
        style_spec=BC.STYLE_SPEC,
        logic_checklist=BC.LOGIC_CHECKLIST,
        out_format='     【疏文】……\n     【記文】……',
    )
```

Wait: BASE_PROMPT principle 2 is: `'2. {book_ctx}{shuji_check}\n'`. With SHUJI_PAIR starting 「【疏】【記】須義理相契：」 directly appended after 「…嚴禁未查即套《隨機羯磨》；」 — reads well.

But the original had bold `**【疏】【記】須雙向互核**` which is a nice emphasis. Should I bold the 相契 phrase? The CTX text is shared with blind/other, so bolding inside constant would leak everywhere. Instead in this module I could do:

```python
SHUJI_PAIR_TEXT = '**【疏】【記】須義理相契**' + SHUJI_PAIR.split('【疏】【記】須義理相契', 1)[1]
```
Ugly. Better leave plain — consistency across pipeline (blind uses plain CTX too) matters more than bold.

prompt_for:

```python
def prompt_for(unit, book=''):
    """依實際單元標籤與書別產生提示詞（避免單邊段出現雙標點與跨欄指示）。"""
    cfg = BC.CFG.get(book or '', {})
    ctx = chk = ''
    if book in ('業疏', '戒疏'):
        if unit == '疏文':
            ctx = SHUJI_BASE
            chk = SHUJI_PAIR + '不得將前後背景中之【記文】專論搬入【疏文】。'
        elif unit == '記文':
            ctx = SHUJI_BASE
            chk = SHUJI_PAIR + '不得以【記文】釋義反向覆蓋所釋【疏文】前提。'
        else:
            ctx = SHUJI_BASE
            chk = SHUJI_PAIR + '依本欄脈絡審校，勿混入背景他欄專論。'
    else:
        ...unchanged...
```

Hmm wait — the `else` inside 業疏/戒疏 covers units like 律文/註文/序文. Should those carry 疏記互核? Probably yes-ish (they're context units from 業疏/戒疏 with paired ji). Keep CTX + generic line.

But is the appended line redundant/conflicting? For 疏文: CTX already says 「但不得將記文專論擴寫搬入疏文」. The extra line emphasizes 前後背景. Slight duplication. Alternative: for single-column branches, apply CTX[0] plus only the branch-specific ban (no CTX[1]) — but then 疏記相契 missing, which was the user's complaint originally? Let me recall summary: "only 單疏 uses SHUJI_CTX[0], others miss 文云 caveat. Need ... add shared SHUJI_CTX caveat to all three".

The user's exact request: 「一審三分支 統一 get_prompt 與 prompt_for 的 SHUJI_CTX」 — unify the SHUJI_CTX usage. The cleanest interpretation: all three branches should embed the same SHUJI_CTX content (both elements), differing only in the one-line 本欄 restriction.

To avoid heavy duplication, I can make the branch line minimal and non-duplicative:

- 疏文: '本欄僅審【疏文】，前後【記文】只作背景，勿將其專論改寫入正文。'
- 記文: '本欄僅審【記文】，釋義與科判動詞不得反向覆蓋所釋【疏文】前提。'
- 疏+記 (get_prompt): no extra line.

That's reasonable.

Now also note `PROMPT = get_prompt(False)` at line 112 stays.

Then check `package_prompts.py` and other callers that may depend on `prompt_for` signature (unchanged).

Potential issue: `prompt_for` is also called for 資持記 via `unit='記文'` but book='資持記' → else branch → unchanged. Good.

Another caller: `_build_review_doc.py` line 148 comment says "尼鈔版由 get_prompt(True)". It renders only get_prompt(False). Should the doc also include the other two branches? Perhaps add 2.2a/2.2b for 單疏/單記? The doc says "一審（疏記版...）". After unification, doc should probably show all three. I could extend the doc builder to render `M.prompt_for('疏文','業疏')` and `M.prompt_for('記文','業疏')`. That makes the unified behavior visible. But minimal: maybe update heading only. The user didn't ask for doc changes. However `_build_review_doc.py` must at least still run. Since get_prompt(False) output changed, rebuild doc at end is expected per prior practice (latest doc rebuild still needed). I'll rebuild after verifying.

Let me now check whether other code asserts exact prompt strings (e.g. tests or `_verify_packing.py`). grep for "疏文與記文" or "雙向互核".