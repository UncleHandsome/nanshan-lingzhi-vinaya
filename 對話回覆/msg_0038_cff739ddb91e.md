# 對話材料 #0038

- event: assistant/message
- seq: 3198
- time: 1793913948213

---

Translations look good quality. Note the text shows 【律】/【註】/【疏】 labels preserved (from source), but our convention in out is 【律文】【註文】【疏文】【記文】. The apply_labels normalizer strips these and re-adds correct labels (since layers.json covers 02_戒疏). But for 資持記/義鈔 there are no labels.

Wait: if the new text starts with 【律】 and layers say 律 → apply_labels would turn it into 【律文】. But apply_labels was already run; after applying miss translations, labels for 20b would be 【律】 (not 【律文】). Need to normalize: either strip 【律】 etc. before writing or re-run apply_labels on 02_戒疏 (which strips and re-adds). But 18b/19b must keep original labels — apply_labels would re-add wrong ones there. Hmm: apply_labels applies to all files; earlier we restored 18b/19b manually. Re-running would break them again.

Options: 
- In apply_miss, for 02_戒疏 strip existing leading label and let a small post-step add correct label from layers for the affected chunk only (20b).
- Simpler: apply translations as-is but convert label with mapping 【律】→【律文】 etc. for 02_戒疏 only.

But wait: 20b layers say 記/疏/律/註 per segment; the translations from agents kept source labels. For 記 segments (source unprefixed), translation has no label → should add 【記文】.

Let me do: after applying, run a targeted label pass for 20b using layers.json (like apply_labels but only that chunk). I'll add a `--only key` option to apply_labels? Quick: write a tiny script.

Also for 資持記 12a/12b: no labels (single layer) — fine.
義鈔: no labels — fine.

Then rebuild site + PDFs? The user said PDFs slowly; after applying, we need site rebuild and PDF rebuild for 戒疏/資持記/義鈔. That's a longer task; can run in background.

Plan:
1. Apply translations (--write).
2. Fix labels for 02_戒疏 20b via layers.
3. Verify counts (verify_counts expects same counts — yes, replacements at same indices).
4. Write miss.txt (already).
5. Rebuild site (fast) + PDFs (background).
6. Update 審校進度 (未譯 counts drop).

Let me apply now.