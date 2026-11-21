# 對話材料 #0853

- event: assistant/message
- seq: 111244
- time: 1795063204121

---

User reports 3 bugs + 2 details from new code:

1. mk_split_blind `_ban` unbound for 疏文 branch — verify: I removed `_ban = ''` from 疏文 branch. Is `_ban` defined before? Code:
```
_bctx = ...
if _lab_full == '疏文':
    _sr = ''
elif _lab_full == '記文' and args.book in ('業疏','戒疏'):
    _sr=...; _ban=''
else:
    _sr=...
    _ban = _cfg.get('shuji_ban','') if _lab_full=='疏文' else ''
if _lab_full not in ('疏文','記文'):
    _bctx=_sr=_ban=''
prompt = ... shuji_ban=_ban
```
Indeed 疏文 branch leaves _ban unset → UnboundLocalError. Fix: set `_ban = _cfg.get('shuji_ban','')` there (restore ban).

2. make_hybrid trim_group unit fallback: `g.get('unit') or '疏文'` wrong for 鈔 books; but groups for 尼鈔/行事鈔/義鈔 have `unit=spec.get('unit')`? Check mk_review BOOKS: 尼鈔/行事鈔/義鈔 have no 'unit' key (only 資持記 unit='記文'). build_groups sets `unit=spec.get('unit')` → None. Then trim sets '疏文'. Fix: `g.get('unit') or ('鈔文' if g.get('no_ji') else '疏文')`. But for paired 業疏/戒疏 groups no_ji False → 疏文 correct. For 記 run we set '記文' explicitly. Good.

Wait also for 鈔 books groups have no_ji=True and unit None → fallback 鈔文. Correct.

3. pack_judge multi-segment dual-column: lab_map merges all 疏文 then all 記文; unmarked 記文 block (記1+記2) all assigned to last _cur_n=2. Need robust fix. Reviewer suggests splitting by [n] blocks before label merging, or detect alternating.

Let me examine current do_split flow around 146-228 to redesign:
- body3 from col3, then L171/172 reorder `[n]\n【lab】` → `【lab】\n[n]`.
- lab_map built by splitting body3 on 【lab】; concatenates per label.
- Then per_group splits each lab chunk by [n].

Problem scenario: model output per segment:
```
[1]
【疏文】疏1
【記文】記1
[2]
【疏文】疏2
【記文】記2
```
But L171 regex `(\[\d+\])\s*(?=【)` inserts newline before 【 when [n] directly precedes label; here [n] on own line followed newline then 【 → L172 moves label before [n]: `[1]\n【疏文】` → `【疏文】\n[1]`? L172 pattern `(?m)^\s*\**\s*\[\s*(\d+)\s*\]\s*\**\s*\n(\s*【...)` replaces with `\2\n[\1]`, yes.
Then body becomes:
```
【疏文】
[1]
疏1
【記文】記1
【疏文】
[2]
疏2
【記文】記2
```
lab_map splits by label occurrences: 疏文 chunk = "\n[1]\n疏1\n"; 記文 chunk = "記1\n"; 疏文 again appended → lab_map['疏文'] = "\n[1]\n疏1\n" + "\n[2]\n疏2\n"; 記文 = "記1\n記2\n". Exactly reviewer scenario → 記1+記2 both to n=2.

Need segmentation by [n] blocks: split body3 by `(?m)^\s*\[\s*(\d+)\s*\]\s*` first, then within each block parse labels. But blocks after reorder start with label then [n]; e.g. `【疏文】\n[1]\n疏1\n【記文】記1\n`. Splitting by [n] gives: before "[1]" block = "【疏文】\n" (label only), block1 content = "疏1\n【記文】記1\n", then before [2] = "【疏文】\n" etc. We can handle: for each [n] block, the label may appear at end of preceding chunk. Simpler: instead of pre-reordering, work on original body3? Original:
```
[1]
【疏文】疏1
【記文】記1
[2]
...
```
Split by `(?m)^\s*\[\s*(\d+)\s*\]\s*` → parts: ['', '1', '\n【疏文】疏1\n【記文】記1\n', '2', ...]. For each block text, parse labels via re.split('【lab】') → per_group[n] gets both labels. This handles both `[n]\n【疏】` and `[n] 【疏】` (same line, since \s* consumes space before label? split pattern ends with \s*, so `[1] 【疏文】` → block starts '【疏文】').

But for non-packed single segment (no [n]), fall back to current lab_map path.

Also some outputs may put label before [n] on same line (`【疏文】[1] 疏`)? Rare; handle by also splitting on `(?m)^\s*【lab】\s*\[\s*(\d+)\s*\]`? Complex. Current reorder handles `[n]` immediately before label only.

Proposed restructure inside do_split:
```
if re.search(r'(?m)^\s*\[\s*\d+\s*\]', body3):
    blocks = re.split(r'(?m)^\s*\**\s*\[\s*(\d+)\s*\]\s*\**\s*', body3)
    # parts: ['', n1, text1, n2, text2...]
    # prefix before first [n] may contain labels only; attach to first block
    for i in range(1, len(blocks)-1, 2):
        n=int(blocks[i]); txt=blocks[i+1]
        # if text starts without label but previous prefix had label? 
        for lab, body in split labels in txt:
            per_group[n].append((lab, body))
    # handle trailing/leading text with labels only?
else:
    old lab_map path
```
But what about prefix `parts[0]` containing labels before first [n] (model writes `【疏文】\n[1]...`)? Reorder L172 may have moved label before [n]; then body3 starts `【疏文】\n[1]...` and split by [n]: parts[0]='【疏文】\n', then block. We should attach parts[0] label to first block. Implement: if parts[0].strip() has labels, parse and prepend to first n.

Similarly trailing text after last block (unlikely).

Also need `_head` handling for lab_map when no markers (single segment): keep old path.

But `_emit_single`/`_jia_group` logic depends on per_group labels; same structure.

Additionally `lab_map` is also used later for `_head` fallback when no segs; restructure carefully.

Let me read do_split 146-240 fully to rewrite section 168-237.