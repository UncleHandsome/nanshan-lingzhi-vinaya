# 對話材料 #0062

- event: assistant/message
- seq: 5053
- time: 1793916610944

---

Both 漏譯 fixed; OCR chars done (僧祗 15 in SRC, 1 in OUT; others).

Wait — 䍃 in 05c: the reviewer said 「水邊䍃䍃者」 is corrupted and should be 「水邊淫…女邊婬…」. Our SRC has 䍃 twice (in the 記 explaining the character). OUT translation says 「䍃」字讀為「婬」... That's actually coherent: 記 is explaining that the character 淫 is 水+䍃 and 婬 is 女+䍃. So 䍃 is correct as a component! The reviewer misread the PDF layout. Leave.

Now: also need to check 【記】 labels now appear in source → but our translations have 【記文】; the source labels are 【記】. Good.

But: adding 【記】 to source lines means build_book/layers? The chunk line counts unchanged. OK.

Also site pages will show 原文 with 【記】 labels.

Next: rebuild 戒疏 docx/PDF/site, update 審校進度, commit.

But the background full rebuild (job pwsh-8c4c7443477d4577) may still be running — it will rebuild 戒疏 from the *current* out/分卷 at its own timing. If I edit now, race conditions. Let me check job status first.

If it's still running, I should wait or kill it, since I've made more changes.

Let me check.