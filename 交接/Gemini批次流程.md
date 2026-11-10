# Gemini Batch 校閱流程

## 送出後檢查節奏（定案）

| 時點 | 動作 |
|:--|:--|
| 送出後 **7 分鐘** | 第一次查詢 |
| 之後 **每 3 分鐘** | 查一次，完成即收結果並刪除排程 |

教訓：先前用「5 分鐘首查、每分鐘追」設定，結果前 10 分鐘都在排隊，白查十幾次。

## 送出前檢查清單

1. **提示詞必須放進 request**：`gem_batch.py` 的 `submit()` 要帶 `prompt_text()`；若靠 cache 帶提示詞，cache 失效時會變成「只送材料」，模型會把原文譯文複述回來（浪費一整輪）。
2. **cache 每次重建**：舊的 `cachedContent` 名稱失效時，API 回 `Could not parse the CachedContent name`，訊息容易誤判為格式錯誤。重建後立刻可用（實測 cached=1,904 tokens）。
3. **記錄 createTime**：從 operation metadata 取 `createTime` 算排程時間，不要憑印象。

## 成本參考（gemini-3.8-flash，2026 年底前）

| 層級 | 輸入 /1M | 輸出（含 thinking）/1M |
|:--|--:|--:|
| Standard | $0.75 | $3.75 |
| **Batch** | **$0.375** | **$1.875** |

實測（20 檔、40 KB／檔）：
- 輸入約 237k tokens、輸出含 thinking 約 285k tokens
- 一輪約 **$0.62**（約台幣 20 元）
- 全書 456 檔一輪約 **$14**，含追問兩三輪約 **$30–42**

thinking 佔輸出約 70%，是最貴的部分。

## 已知失敗模式

| 症狀 | 原因 |
|:--|:--|
| 20 個請求全 `invalid argument` | 帶了失效的 cachedContent |
| 回應是【原文】【譯文】照抄 | request 裡沒帶提示詞 |
| 長時間 pending | batch 排隊，正常現象（10–20 分鐘） |
