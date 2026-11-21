# 對話材料 #0786

- event: assistant/message
- seq: 107519
- time: 1795047547673

---

Now edit the get_prompt/prompt_for block. Replace lines from `def get_prompt(is_nicao=False):` through the end of `prompt_for` (before `PROMPT = get_prompt(False)`).

Old block (as read earlier, with line numbers 57-109). Let me write the replacement.

Note: I'll add module constants right after BASE_PROMPT:

```python
# 一審三分支（疏＋記／單疏／單記）共用同一套文注脈絡與疏記互核規範
SHUJI_BASE, SHUJI_PAIR = BC.SHUJI_CTX
```

Where to put? After BASE_PROMPT definition, before get_prompt. Good.

Replacement text:

```python
# 一審三分支（疏＋記／單疏／單記）共用同一套文注脈絡與疏記互核規範
SHUJI_BASE, SHUJI_PAIR = BC.SHUJI_CTX


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


def prompt_for(unit, book=''):
    """依實際單元標籤與書別產生提示詞（避免單邊段出現雙標點與跨欄指示）。"""
    cfg = BC.CFG.get(book or '', {})
    ctx = chk = ''
    if book in ('業疏', '戒疏'):
        ctx = SHUJI_BASE
        if unit == '疏文':
            chk = SHUJI_PAIR + '本欄只審【疏文】，前後【記文】僅作背景，勿將其專論改寫入正文。'
        elif unit == '記文':
            chk = SHUJI_PAIR + '本欄只審【記文】，釋義與科判動詞不得反向覆蓋所釋【疏文】前提。'
        else:
            chk = SHUJI_PAIR + '依本欄脈絡審校，勿混入背景他欄專論。'
    else:
        if unit == '鈔文' and cfg.get('note'):
            chk = cfg['note']
        elif unit == '記文':
            chk = ((cfg.get('note', '').rstrip('。；') + '；') if cfg.get('note') else '') + \
                  '**【記文】須與所釋《行事鈔》及本記前後文脈相契**：不誤導、亦不隱沒所牒實詞。'
    return BASE_PROMPT.format(
        scope=unit, split_target='【%s】' % unit,
        book_ctx=ctx, shuji_check=chk, logic_checklist=BC.LOGIC_CHECKLIST, style_spec=BC.STYLE_SPEC,
        out_format='     【%s】……' % unit)
```

Wait — for 業疏/戒疏 `unit` could be 律文/註文/序文; `else` branch handles that.

One question: in `prompt_for` for 資持記 記文 branch, cfg is 資持記 with JI_NOTE; unchanged behavior. Good.

Now: does `SHUJI_BASE` contain leading part '《業疏》所釋「文／注」指…' — yes.

Let me do the edit, replacing from `def get_prompt` to `out_format='     【%s】……' % unit)`.