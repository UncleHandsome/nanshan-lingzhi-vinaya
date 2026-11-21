# 對話材料 #0086

- event: assistant/message
- seq: 28876
- time: 1794087401933

---

No massive duplication in out. So the report's "1083 段 completely misaligned/repetition" must come from the pack generation being wrong for that particular pack — likely the 鈔記 paired sequence (maoji_items) is misaligned!

Wait, but the report mentions 疏/記 pairs (#疏/#記), so it's likely a 鈔記 pack... Actually "【疏】善見》不請起過者" — that's 戒疏 (疏). And "【記】釋疑中初問" — 戒疏 has 記? Yes! 戒疏's chunks contain 【疏】【記】 labels (we saw out/02_戒疏/19a has 【律文】/【疏文】/【記文】). So 戒疏 itself is 疏+記 interleaved.

So a 戒疏 pack: my book_items pairs src line i with out paragraph i. If out 戒疏 has 【記文】 paragraphs corresponding to src 【記】 lines, index pairing should be right.

But the report shows blocks where many segments share the same translation — which does NOT exist in out. So the pack generation must be duplicating.

Look at review_pack.book_items: for i in range(min(len(sp),len(tp))): append. That's index pairing — no duplication.

Unless... `tr_paras` re.split on `\r?\n\r?\n` gives right; no duplication.

Hmm, but maybe the pack file itself was generated from an older out state where duplication existed? No.

Wait — maybe the report is about a *different* pack: the user might be feeding the 650K packs which include 鈔記 sequence from maoji_items. In maoji_items, I pair 鈔 with 記 via bounds but emit items in sequence — for 記 items, orig/trans come from Z[p] (correct); for 鈔 items from S[p].

But there's a bug: `idx` mapping for 鈔 uses TXT_分卷 source, and `S[p]['items']` are 鈔 paragraphs with translations; pairing is consistent.

Hmm, but what if `S[p]['items']` and `Z[p]` indices don't align as I think, causing 記 orig paired with 記 trans — still consistent.

The reported symptom "同一段譯文重複幾十次" can't come from my packer unless input had it.

Unless the user's AI hallucinated the whole structural analysis! That's plausible: the model saw a large batch, got confused, and invented a "systematic alignment failure" narrative. The evidence: it claims 1083/1186 misaligned with specific block patterns — that's a classic LLM confabulation when input is too long (65K→325K chars, ~200K tokens), exceeding context and causing repeats/truncation internally.

We cut size to 325K chars (~500KB bytes) — still huge for many models (~200k+ tokens). DeepSeek 128k context would truncate → model sees corrupted/repeated content → reports misalignment.

So the likely cause: **file too large for the model's context**, not data corruption.

Evidence to verify: take the pack file the user used, locate the claimed block (段020-090 all same translation). Check whether pack file actually has repeated translations there. If not → the AI hallucinated/truncated.

Let me verify: search pack for consecutive identical translations. Use script: for each pack file, count consecutive duplicate 譯文 lines.

If packs are clean → answer: batch files are fine; the AI's context overflowed.

Let me check.