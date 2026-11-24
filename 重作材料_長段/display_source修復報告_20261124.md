# display_source／source 骨架 corruption 修復報告（2026-11-24）

## 問題

部分段落的原文變成「標點骨架」：漢字被吃掉，只剩 `《》，。《》：，，，。，，，，。` 這類標點殘骸，
或留下空引號 `「」`、空書名號 `《》`。來源是上游句讀語料本身已有骨架區，
早前建立 display_source 時把骨架區一併抄入；少數段的 source 也被污染。

## 檢查範圍

六書定稿全部 row 與 segment：

- `han(display_source) != han(source)`
- `is_skeleton`：漢字密度過低、連續標點叢、空括號對

## 修復

1. `_src/fix_display_source.py`
   - 以 source 漢字序列在句讀語料中唯一搜尋，取回含標點原文重建 display_source。
   - 語料命中區若本身是骨架（密度／空括號檢查）→ 拒絕，換下一個語料。
   - 合併列用 greedy 片段重組；底本用字與語料不同時用序列比對轉移標點（保留底本字）。
2. `_src/fix_skeleton_sources.py`
   - source 漢字完整（純標點骨架）→ 直接取語料句讀。
   - 空引號 → 用 raw 上下文補回被吃掉的引文用字。
   - 前後錨點 → 從 raw TXT 還原完整原文。
   - `07b_卷二之一_0016` 底本原字即「二約位定人，二約法定用」，只補標點、不從句讀本改字。
3. `07a_卷二之一_0021`  targeted 修復：source/display 補回「者是也」，raw 邊界對齊。

## 結果

```text
六書 row＋segment 骨架／空括號／漢字不一致：0
網站 pairs 29582、search 29557、punct 0、errors 0
3K 材料 7468 檔，全部通過骨架 pattern 掃描
```

備份：`定稿/_舊_<book>_before_dispfix_20261124.jsonl`

## 尚未處理：上游語料骨架區

以下語料檔本身仍含骨架區（本次修復已繞過，改用 TXT_句讀 或 raw 還原）：

```text
TXT_句讀校定/yeshu.txt                 9 區
TXT_分卷_標點/03_業疏/04b_卷一之四.txt   1 區
TXT_分卷_標點/03_業疏/07b_卷二之一.txt   3 區
TXT_分卷_標點/03_業疏/16a_卷三之五.txt   1 區
TXT_分卷_標點/03_業疏/16b_卷三之五.txt   1 區
TXT_分卷_標點/03_業疏/18a_卷四之一.txt   1 區
TXT_分卷_標點/03_業疏/18b_卷四之一.txt   1 區
TXT_分卷_標點/03_業疏/20b_卷四之三.txt   1 區
```

若日後要從這些語料重新產生 display_source，需先修復語料骨架區，否則會再次引入殘骸。

---

## 後續：順序對齊＋語料修復（同日完成）

### 六書重新順序對齊原文（_src/realign_raw.py）

以 TXT 底本漢字序列（只計 4e00–9fff，與渲染器 hpos 一致）重算 raw_start／raw_end，
依原文順序排序定稿列。不改 source／translation／segments。

```text
行事鈔   2134 對齊、7 合併列取涵蓋區間、1 未對齊（192）
戒疏     4563 全對齊
業疏     2716 對齊、1 修正（07a_0021）、8 合併列、3 未對齊（0047/0046/09a_0008）
尼鈔     1100 全對齊
義鈔     508 對齊、1 合併列
資持記   4182 座標系自成一套，僅驗證順序（單調 ✓）
```

未對齊的 4 列是疏記合併列，source 非底本連續片段，保留原位置。
備份：定稿/_舊_<book>_before_realign_20261124.jsonl

### 上游語料骨架修復（_src/fix_corpus_skeleton.py）

用 TXT_句讀/03_業疏（genuine）对应區段置換骨架區，前後 12 漢字錨點對齊：

```text
TXT_句讀校定/yeshu.txt                9 區 → 0
TXT_分卷_標點/03_業疏/04b,07b,16a,16b,18a,18b,20b  共 9 區 → 0
```

全部語料復掃：骨架區 0。備份：各檔 .bak_skeleton_20261124。
注意：置換採用句讀本用字（與底本偶有異文，如「次」字有無）；定稿 display 仍以底本為準。

### 重建驗收

```text
網站 pairs 29582、search 29557、punct 0、errors 0
3K 材料 7474 檔
```
