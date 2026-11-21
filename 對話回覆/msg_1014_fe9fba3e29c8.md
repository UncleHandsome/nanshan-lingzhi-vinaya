# 對話材料 #1014

- event: assistant/message
- seq: 124266
- time: 1795217853305

---

Now website fully updated incl search. Need verify no extra page, no links; index still link only 卷上/卷中; nav updated. Check `docs/search/yichao.js` prefix, page pair IDs, search href. Also maybe `docs/search/manifest.js` still book; fine.

Need remove `docs/yichao/長段對照.html` (already deleted; check). `docs/index.html` no link. `nav.json` no long entry. Good.

Need maybe **update `docs/yichao/卷上.html`/`卷中.html` top links** gone because main replaced; yes.

Need perhaps **update `docs/index.html` card** no long; yes.

Need **test page** with search anchor `s1`; HTML contains id; search index i; good.

Need **website page content** now includes 225/144 pairs, total 369; source+final. Good.

Potential issue: `sid` global across volumes; search entries `i=s1...`; pages have IDs; fine.
- `v` values `卷上`/`卷中`; search href `yichao/卷上.html#s1`; correct.
- Search entries `o` includes `■`/`【鈔文】`; okay.

Need **update `docs/index.html`** if earlier link removal; verify.