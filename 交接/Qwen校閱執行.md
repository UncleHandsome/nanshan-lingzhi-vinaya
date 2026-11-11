# Qwen 校閱執行方式

## 啟動

```powershell
$env:QWEN_WORKERS=12
python -X utf8 _src\qwen_review.py 1 1912
```

- 會自動跳過已有結果的檔案（可續跑）
- 併發預設 12（可用 `QWEN_WORKERS` 覆寫）

## 優雅停止（不浪費在飛請求）

```powershell
New-Item -ItemType File batch_qwen\STOP
```

程式會在下一輪檢查時：

1. **不再送出新請求**
2. **等待已在飛的請求寫完**
3. 印出「收到停止訊號，等待 N 個在飛請求完成…」後才結束

恢復時把 `STOP` 刪掉即可重新啟動。

## 為什麼不直接 kill

直接 kill 會讓當下 24–32 個在飛請求全部作廢（已付費但沒結果）。用 STOP 檔可把損失降到零。

## 其他

- 輸出：`batch_qwen/r1/resp_NNN.txt`
- 429 會自動退避重試 3 次
- 失敗檔會印出行號，可事後重跑
