# 對話材料 #1078

- event: assistant/message
- seq: 129624
- time: 1795236870559

---

User wants 業疏 processed in one go. Need rebuild full 業疏 with general 2,580 + 5 long sections (04b 4? others 14) + labels? 業疏 likely `【疏文】`/`【記文】` labels too? User wants one-time.

Current pages 2,580 units (post 9853ac4) with 04b new distributed? We reverted to 9853ac4 then 04b distributed `00d879d` (卷一 680); other four not. But then later jieshu commits don't affect yeshu; current yeshu pages: 卷一 680 (04b distributed), 卷二 572? full general, 卷三 706, 卷四 622. Need one rebuild including:
- 2,580 general units from `_終審` PASS + replies
- 5 long sections: 00 5, 16a1, 18a5, 18b3, 04b 4 (or 85 fine?) User earlier said don't merge; 04b should remain **85 fine units** with translation distributed. For one rebuild, ideally include long sections as **fine segments** (source split into 8?); we have 04b 4 blocks but user wants split; we distributed into 85 existing units, but rebuild from `_終審` may not include 04b units. Hmm.
- Could rebuild general 2,580 + insert long sections **sentence-level split** (split each final block into sentences) so no big merge; 04b into 85? Hard.

Maybe "一次處理到好" means combine all 5 long + general; use 04b 4 blocks but user just objected merging. Need preserve fine split:
- For each long section, split source/translation into sentences/paragraphs, create small pairs; insert at correct positions. This is one rebuild, no merge.
- General 2,580; long 00/16a/18a/18b/04b; split finals into sentences; source split by punctuation.
- Insert by raw order; h2; labels `【疏文】`/`【記文】`? 業疏 likely source units contain `■`; add labels? Maybe.
- This is a lot but can build.

Simpler: Build from `_終審` 2,580, and **insert long sections as fine sentence pairs** at raw positions:
- Use final translations for 5 keys; split each into sentences; source split into equal sentences? Source long blocks; split by punctuation; pair sentence i to translation i? Counts differ. Could split source into paragraphs and translation into same number by sentence grouping; approximate.
- 04b 4 blocks; split into 8/10 small pairs, not 85; user wanted no merge, small segments okay.
- But "細切" may mean preserve 85 units; better use current pages 04b distributed 85 and add other 4; but one rebuild from current pages + 4 longs (not 04b) is easier:
  - Current 卷一 has 04b distributed (85 fine), 680 pairs.
  - Current 卷二/三/四 general; add 00/16a/18a/18b as **sentence-level small pairs** at positions.
  - But general 2,580 current pages? 卷一 680 after 04b; others 572/706/622; total 2,580? 680+572+706+622=2,580; 04b distribution replaced 85 same count, so total 2,580.
  - Add four long sections by splitting their finals into sentences; insert; total >2,594; no merge.
- This is "one go" for remaining 4, not full general? General already.

Need decide implementation. User likely wants all 業疏 long integrated; do a rebuild from current pages + four long sections split into **sentence pairs**, preserving 04b fine.

But current pages h2 45? Yes.
- Add 00 (5 blocks), 16a(1), 18a(5), 18b(3); if split each into sentences, many pairs.
- Source split by punctuation into sentences; translation same count? Need pair; can split final translation into N sentences and source into N; use source sentences and translation sentences; if counts mismatch, allocate.
- Or keep blocks but split each into **paragraph pairs**; not merge? 5 blocks are already smallish; user complained merging 04b into 4, so 5/1/5/3 may be okay? They said "長段不要合併"; perhaps 5 is fine, 4 was too coarse. Keep 5/1/5/3 as separate pairs, not one; insert. That's acceptable.
- Add four long blocks with labels, preserve h2; no merge. Current 04b fine.

Do merge four into current yeshu pages (like previous) but **do not merge 04b**; add 00/16a/18a/18b 14 pairs; sort; h2. We attempted before; targets absent; insert by raw. This yields total 2,594; 04b fine.
- Need h2 preserve; use current h2 titles; add.
- Counts 卷一 685? 00 5; 卷三 707; 卷四 630.
- This is "one go" for remaining; no big block merge (each long output block separate; 18a 5 blocks, etc.).

Let's implement with current pages; add four; sort; h2; commit.