# 對話材料 #1271

- event: assistant/message
- seq: 135895
- time: 1795250574439

---

Need continue 戒疏 sequence alignment; 7,605 pages, 7,367 matched, 238 unmatched, gaps257, overlaps112. Need figure why 238 unmatched and gaps. Could inspect mapping/JSON and page sources; maybe h2/chunk ordering not raw, or page duplicates. Need diagnose, not mechanical.

Read `戒疏_sequence_map.json`; compare current pages order vs mapping; identify unmatched pages and gaps; perhaps page order has **front matter and TOC** then categories; 238 unmatched may be **duplicate/short** or pages with source not in raw due variants. Gaps 257 likely because matched pages cover only portions, but raw has long prefaces/記文 not in page.

We need answer "到底怎麼回事" with concrete.

Compute:
- Parse current 戒疏 pages 7,605; sequence map matched 7,367.
- Unmatched sources list (238) lengths/samples; classify:
  - source not found in raw at all (miss) vs found but not in monotonic chain (out-of-order).
  - Our DP map only matched; need rerun to capture candidates/why.
- Gaps 257: raw intervals not covered; lengths/total; classify large vs headings, duplicates.
- Overlaps 112: true? from matched intervals.

Could use mapping JSON and pages; unmatched = pages not in map by source? Map data keyed only src/pos, no page index; duplicates source may collide. Need rerun diagnostic with page index and candidate info, but time.

Alternative answer based on rates:
- 238/7605 (3.1%) not in monotonic sequence; mostly source not in raw due **戒疏 page sources include `【律文】`/`【註文】` from long sections or variants**, or front matter.
- Gaps 257: raw includes **CBETA prefaces/目錄** not in pages, plus source segments not covered.
- 112 overlaps likely repeated formulas; need classify.

Need actual root cause: We earlier global coverage for 戒疏 had 0 notfound/0 gaps? After 16 splits, counts 7,576 and coverage check said 0 none, dec0 using volume ranges; sequence alignment across raw now gaps257. Why discrepancy? Because previous check used **volume ranges and `h.find` global**, not monotonic; sequence DP changes.

Maybe 戒疏 pages include **all source but sorted by chunks that don't align to raw**; mapping can't fit 238 pages due repeated phrases; gaps are raw segments omitted.

Need inspect first 10 unmatched/gaps from a diagnostic. Could run a simpler script:
- Parse pages, find candidates; map from JSON positions; unmatched pages = no pos / not in map. Print first 20.
- Gaps from mapping coverage; print first 10.
We can reconstruct intervals from JSON (src,pos) but JSON may duplicate; use.
Need page order/keys; map JSON lacks keys; add index? We can rerun but slow? 7.6k fast.

Given user demands, do diagnostic via script:
- Read `戒疏_sequence_map.json` (matched src/pos).
- Build pages; mark matched by (src,pos?) not unique; simpler use JSON positions; coverage gaps.
- For unmatched, page src not in map src set (may match duplicates).
- Print first 20 unmatched lengths/samples.
- Gaps raw text first 10.
This yields evidence.

Let's run.