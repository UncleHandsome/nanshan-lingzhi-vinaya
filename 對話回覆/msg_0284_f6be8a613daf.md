# 對話材料 #0284

- event: assistant/message
- seq: 63713
- time: 1794657437054

---

Now remaining from user's list:
- 資持記 unit/format (mk_review_materials: 資持記 shu=None ji=None → unit 鈔文; mk_split_blind nicao=False → format 疏+記).
- mid-length 141–500 疏/記 and unpaired 律/註/序 in 業疏/戒疏 dropped.
- load_pair warning.
- audit/revise try/except actual usage (my col3_safe added but not used).
- 審核 NO_CITE docs.

Let me handle:

1. mk_review_materials: add book-specific handling:
   - For 資持記: unit should be 記文; treat as segment mode but label '記文'.
   Changes: in emit(), unit = '鈔文' if no_ji else '疏文'. Add BOOK-aware: if spec book 資持記 → unit '記文'; prompt should be for 記文 only? BASE_PROMPT scope 疏文與記文 is okay-ish, but better a 記文-only variant.
   Simpler: for 資持記 set shu='記', ji=None and pairing logic? Complicated.

Given time, minimal viable: add `--unit-label` override? Hmm.

Alternative: exclude 資持記 from this pipeline (it's a 記 text; translation of 資持記 can be handled as 記文 with shu=None but label 記文).

Implement: BOOKS entry add key 'unit' e.g. '記文'; in emit, unit = spec.get('unit') or ('鈔文' if no_ji else '疏文'). And get_prompt needs a 記文-only variant: get_prompt(False) includes 疏記; for 記文-only we can reuse nicao-like variant with label 記文.

Add get_prompt(mode) supporting '記文'? Let me add param unit.

Time is a factor; implement a focused patch:
- BOOKS: 資持記 add unit='記文'.
- build_groups: for that book, no_ji True but lab '記'.
- emit: unit from spec; when unit=='記文', prompt = M.get_prompt(False) but replace 【疏文】 mentions? Simpler: create get_prompt_ji() that formats BASE_PROMPT with scope='記文', split_target='【記文】', out_format='     【記文】……', extra_ban etc. empty.

Similarly mk_split_blind for 資持記: fmt '【記文】……'.

2. mid-length and unpaired: raise max_shu/max_ji to 500 for 業疏/戒疏 (paired), and add segment-mode fallback for unpaired 律/註/序? That's a bigger feature.

Pragmatic: raise max to 500 so 141–500 included; unpaired 律/註/序 remain excluded — document as known gap, since those are 戒本註 etc.

Given time, do: max_shu=500, max_ji=500 for 業疏/戒疏.

3. load_pair warning print.

4. audit/revise: wrap iteration body in try/except. Simplest: replace col3(rt) calls with col3_safe and skip None.

Let me implement.