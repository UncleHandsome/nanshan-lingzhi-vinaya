# PDF 閱讀器式版面報告

> 對象：`docs/` 靜態網站（南山律典・白話對照，48 頁）
> 日期：2026-11-23
> 執行：web-reader（subagent）
> 依據：`AGENTS.md` §0.8、§6；`重作材料_長段/網站頂部收窄報告.md`
> 限制：**未手改任何 `docs/**/*.html`**；只改 `_src` 生成器／CSS／JS 後重建。未動 canonical 資料、未跑 qwen、未 import `site2.py`。

---

## 0. 結論

1. **閱讀工具常駐**：移除「閱讀工具」按鈕與下拉面板，`原文＋白話／原文／白話／並排／複製` 五個控制直接排在頂部列右側，桌面與手機都不再需要點開。
2. **分卷導覽上移**：頂部列順序改為 `☰ 目錄 → ← 上一卷／目前卷／下一卷 → → 書名・卷 → 全域搜尋 → 閱讀工具`；首卷隱藏上一卷、末卷隱藏下一卷。側欄的「分卷」群組完全移除。
3. **側欄只留目錄**：書目下拉＋卷／篇 TOC；首頁與非書頁只列書目，不再顯示書目→卷的展開清單，也不顯示空 TOC。側欄沒有搜尋輸入、沒有「全書」連結列。
4. **PDF reader 版型**：左 280px 目錄、上 45px 工具列、中央 960px 正文；桌面 1440 全部一行，390 為兩排（上排目錄＋分卷＋搜尋，下排常駐工具），沒有水平溢出。
5. **驗收**：`validate_site.py` **0 errors**；pair **26,712**、search **26,687** 與改動前一致；Playwright **218/218** 檢查通過；48 頁 × 1440／390 共 96 次載入，0 頁水平溢出。

---

## 1. 改動

### 1.1 原始碼

| 檔案 | 改動 |
|:--|:--|
| `_src/site_assets.py` | `ASSET_VERSION 26 → 27`；`tools_html()` 移除 `hidden` 與分段 wrapper，改成常駐 `.tb-readtools`（3 個顯示模式＋並排＋複製）；新增 `volnav_html()`；`topbar_html()` 參數加入 prev／next，順序改為目錄→分卷→書名・卷→搜尋→工具；`nav_parts()` 移除側欄「分卷」群組；`page()` 對有工具的頁面加 `page-reader` class（供手機兩排高度使用） |
| `_src/site.css` | 頂部列由 grid 改 flex；新增 `.tb-volnav`／`.tb-vol`／`.tb-volcur`、`.tb-readtools`／`.tb-seg`；移除 `.tb-more*`、`.tb-tools*`、舊 `.toolpanel` 絕對定位下拉與 `.tp-row`／`.tp-div`；新增首頁 `.navbooklist`／`.navbookitem`；新增 ≤900px 兩排頂部列（`--topbar-h: 74px`）與 ≤700px 精簡規則 |
| `_src/nav.js` | `renderHome()` 改成只輸出書目清單（不展開卷）；移除 `setToolsOpen()`／`closeTools()`、工具按鈕事件、點外面收起、`moreMenu` 全部邏輯；`initReadTools()` 只綁常駐工具列；Esc 只處理 peek／抽屜 |
| `_src/render_static.py` | 首頁「附錄」旁補「未譯段落清單」連結；原本「更多」下拉移除後，全書入口仍可從首頁／搜尋頁到達 |

> 未改 `render_canonical_cb.py`、`render_zhichi.py`、`site_hebian.py`；六書與合編頁面只由原生成器重建，沒有 regex patch HTML、沒有手工錨點。

### 1.2 產物

- 48 頁 HTML 全部重建，全部為 `style.css?v=27`、`nav.js?v=27`。
- `docs/style.css`、`docs/nav.js` 同步為 v27；`docs/search/*.js` 重建後內容不變（search 26,687 筆）。
- 有 `.pair` 的 44 頁書頁／合編頁：1 個常駐 `#toolpanel`、5 個工具按鈕、`body.page-reader`。
- 首頁／搜尋／附錄／未譯：無 `.pair`，不輸出閱讀工具（避免空操作按鈕），頂部列只有目錄／書名・頁名／搜尋。

### 1.3 重建順序（實際執行）

```powershell
python -X utf8 _src\render_static.py
python -X utf8 _src\render_canonical_cb.py --apply
python -X utf8 _src\render_zhichi.py
python -X utf8 _src\render_zhichi.py --apply
python -X utf8 _src\make_hebian.py
python -X utf8 _src\build_search_index.py
python -X utf8 _src\validate_site.py
```

重建前已把 `docs/` 備份到 `%TEMP%\docs_backup_pdfreader_20261123_212454`；全程未 import `site2.py`。

---

## 2. 量測

### 2.1 桌面 1440（行事鈔卷中，Playwright／Chromium）

| 項目 | 量測 |
|:--|--:|
| `.topbar` 高度 | **45px**（≤48） |
| sticky | 捲到 `scrollY=1400` 後 `top=0` |
| `.tb-volnav` | **156.9×30**（← 卷上／卷中／卷下 →） |
| `.tb-volnav`（首卷） | 99.1×30（只有目前卷＋下一卷） |
| `.tb-crumb` | 729.8×23.1（書名・卷） |
| 全域搜尋輸入框 | **200×30**，`x=979.3` |
| `.tb-readtools` | **248.75×30**，`x=1182.5 / right=1431.2` |
| 工具按鈕 | 5 個：`原文＋白話`、`原文`、`白話`、`並排`、`複製` |
| 側欄 | 280px（固定，`top=45`） |
| 正文 `main` | 960px（`x=380`） |
| 水平溢出 | **0**（`scrollWidth=1440`） |
| 深連結 `#p3` | `top=57.2`（45＋12，未被頂部列遮住） |

### 2.2 手機 390（行事鈔卷中）

| 項目 | 量測 |
|:--|--:|
| `.topbar` 高度 | **74px**（兩排） |
| 上排 | `☰ 目錄` 61.1×32、`.tb-volnav` **146.4×30**、`搜尋` 39.8×32 |
| 下排 `.tb-readtools` | **377.2×30**，`x=6.4 / right=383.6` |
| 五個工具按鈕 | 同一排，`x=155.0 … 383.6`，全部在視窗內 |
| 水平溢出 | **0**（`scrollWidth=390`） |
| 抽屜 TOC | 寬 **340px**、`top=74`、書目下拉＋3 卷（卷上／卷中／卷下） |
| 抽屜開啟 | 點 `☰` 後 `body.nav-drawer-open`、scrim 出現；Esc 關閉 |
| 深連結 `#p3` | `top=86.2`（74＋12） |

### 2.3 寬度掃描（同頁 320–1440）

| 視窗寬 | 書頁頂部列高 | 首頁／附錄頂部列高 | 水平溢出 |
|--:|--:|--:|:--|
| 320 / 360 / 390 / 700 | 74px（兩排） | 46px | 0 |
| 901 / 1024 / 1100 | 46px（單排） | 46px | 0 |
| 1200 / 1440 | 45px（單排） | 45px | 0 |

### 2.4 全 48 頁掃描

- 48 頁 × 1440／390 共 **96 次載入**：0 頁水平溢出。
- 靜態掃描：48/48 頁各有 1 個 `.topbar`、1 個 `#navtree`；44 個書頁各有 1 個 `#toolpanel`、5 個工具按鈕；沒有 `.tb-more`、`data-tools-toggle`、`#toolstoggle` 殘留；沒有 `.new` 檔。
- 首頁／非書頁：`#navtree` 只有 `.navbooklist`，0 個 `details.vol`；書頁：`.navbookpick`＋卷 TOC，0 個側欄 `.grp`。

### 2.5 `validate_site.py`（0 errors）

```text
pages 44 (all html 48) anchors 185 pairs 26712 brbr 0 punct 0 search 26687 searchbad 0 errors 0 warns 6 v27
```

- pair **26,712**、search **26,687** 與改動前完全一致。
- 6 個 warn 都是既有的大頁面體積警告（戒疏 4 卷、業疏卷三、合編卷上之一），不是本次新增。

### 2.6 互動檢查

- **分卷**：行事鈔卷上按「下一卷」→ `卷中.html`；卷上沒有「上一卷」、卷下沒有「下一卷」；合編卷上之一→卷上之二正常。
- **閱讀模式**：`原文` 加 `hide-t`、`白話` 加 `hide-o`、`原文＋白話` 兩者都移除；localStorage 記憶正常。
- **並排**：1440 可切換 `html.twocol`，正文變兩欄（截圖 81）。
- **抽屜**：390 開／Esc 關正常，抽屜內書目與卷／篇 TOC 都在。
- **深色**：1440 深色模式下 topbar 45px、工具常駐（截圖 82）。

---

## 3. 截圖

目錄：`重作材料_長段/_網站截圖_改善後/`（19 張）

| 檔名 | 內容 |
|:--|:--|
| `70-desktop-1440-index-reader.png` | 首頁 1440：45px 頂部列、sidebar 只有書目 |
| `71-desktop-1440-xingshichao-reader.png` | 行事鈔卷上 1440：分卷、書名・卷、常駐工具 |
| `72-desktop-1440-jieshu-reader.png` | 戒疏卷一 1440 |
| `73-desktop-1440-yeshu-reader.png` | 業疏卷一 1440 |
| `74-desktop-1440-zhichi-reader.png` | 資持記上一上 1440 |
| `75-desktop-1440-nicao-reader.png` | 尼鈔卷上 1440 |
| `76-desktop-1440-yichao-reader.png` | 義鈔卷上 1440 |
| `77-desktop-1440-hebian-reader.png` | 合編卷上之一 1440 |
| `78-desktop-1440-search-reader.png` | 搜尋頁 1440（無閱讀工具，保留大型搜尋框） |
| `79-desktop-1440-appendix-reader.png` | 附錄 1440 |
| `80-desktop-1440-untranslated-reader.png` | 未譯清單 1440 |
| `81-desktop-1440-tools-active.png` | 閱讀模式＋並排作用中（1440 兩欄） |
| `82-desktop-1440-dark-reader.png` | 深色模式 1440 |
| `83-mobile-390-index-reader.png` | 首頁 390：46px 單排、sidebar 只有書目 |
| `84-mobile-390-xingshichao-reader.png` | 行事鈔卷上 390：兩排、分卷可見 |
| `85-mobile-390-tools-reader.png` | 手機常駐工具列（五個按鈕同一排） |
| `86-mobile-390-drawer-reader.png` | 手機抽屜：書目下拉＋卷／篇 TOC |
| `87-mobile-390-search-reader.png` | 搜尋頁 390 |
| `88-mobile-390-hebian-reader.png` | 合編卷上之一 390 |

原始量測：`重作材料_長段/_網站截圖_改善後/_驗收數據_PDF閱讀器.json`（218 checks／0 fail、寬度掃描、48 頁掃描）。

---

## 4. 驗收對照

| 驗收項 | 結果 |
|:--|:--|
| 1440 topbar ≤48px | **45px** |
| 1440 工具全部直接可見 | 5 個按鈕常駐，無 toggle／下拉 |
| 1440 分卷上一／下一可用 | 中間卷雙邊可點；首末卷單邊隱藏 |
| 1440 sidebar 無「分卷」群組 | 0 個 `.grp`、無「分卷」文字 |
| 1440 無水平溢出 | 48 頁 × 1440 掃描 0 |
| 390 無溢出 | 48 頁 × 390 掃描 0 |
| 390 工具與分卷可用 | 工具同一排、分卷可點、抽屜可開 |
| 390 閱讀工具不是下拉 | 常駐 `.tb-readtools`，無 toggle |
| 首頁 sidebar 只留書目 | `.navbooklist`、0 個 `details.vol` |
| 書頁 sidebar 書目＋TOC | `.navbookpick`＋卷 details（各書 2–16 卷） |
| 搜尋／全書連結不在 sidebar | 0 個 `search.html` 連結、無「全文搜尋」文字 |
| `validate_site.py` | **0 errors**；pairs 26,712；search 26,687 |
| ASSET_VERSION | 26 → **27**，48 頁全 v27 |
| 截圖 | 19 張（桌面 1440／手機 390／深色／六書＋合編） |

---

## 5. 殘留

1. **非閱讀頁不顯示閱讀工具**：首頁／搜尋／附錄／未譯沒有 `.pair`，因此不輸出 `原文／白話／並排／複製`；這些控制在該頁沒有作用對象，寧可不出現。若要求首頁也看到工具列，需另做 disabled 版本，會多一排無效控制。
2. **「並排」在 <1200px 仍停用**：這是原本行為（手機兩欄不可讀）；390 仍看得到按鈕但為 disabled。其餘四個控制（原文＋白話／原文／白話／複製）在 390 可用。
3. **手機 ≤700px 隱藏麵包屑**：390 上排只有目錄＋分卷＋搜尋，書名／卷名由正文 `h1` 呈現；分卷控制仍完整可見。701–900px 保留書名・卷。
4. **桌面書名與右側工具有較大彈性空白**：`.tb-crumb` 吃掉中間剩餘寬度，這是「左目錄／中書名／右工具」的版型結果；若要壓掉空白，可把書名改成固定寬或靠右，但會偏離指定順序。
5. **底部卷末 pager 保留**：`validate_site.py` 要求每頁有 `<nav class="pager">` 與 rel=prev/next；本次未移除，功能上與頂部分卷重複。
6. **首頁書目連到各書第一卷**：沒有另做「書本 landing page」；書目清單的每一列直接進該書第一卷。
7. **未做 Firefox／Safari 實測**：以 Chromium headless 量測；`:has` 未使用，`position:sticky`、`100dvh`、`inert` 在現行版本皆支援。
8. **截圖需 HTTP 伺服器**：`nav.json` 用 fetch 載入，直接開 `file://` 會顯示「目錄載入失敗」；本次全程用 `python -m http.server 8765`。

---

## 6. 回滾

```powershell
git checkout -- _src/site_assets.py _src/site.css _src/nav.js _src/render_static.py docs
```

回滾後以 v26 生成器重跑 `render_static.py`、`render_canonical_cb.py --apply`、`render_zhichi.py`＋`--apply`、`make_hebian.py`、`build_search_index.py`；不要用 `site2.py` 當回滾手段。

> 提交：`site: 改為 PDF reader 式版面（常駐工具、分卷上移、側欄只留 TOC）`（只 stage 網站原始碼、48 頁產物與本報告）。
