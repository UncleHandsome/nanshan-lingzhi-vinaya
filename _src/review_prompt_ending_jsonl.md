（三）JSONL 結構化結果：在文末輸出以下固定錨點區塊，每個輸入段落對應一行 JSONL（勿加 code fence）。status 判定規則：全段無誤填 "ok"；確有須修且無任何「存疑待查」處填 "fixed"；凡含任何「存疑待查」處（含兼有確定誤譯之混合段），為避免未經確認之譯文自動發布，整體一律填 "uncertain"：

<<<JSONL_START>>>
{"key":"僅填##後的純代號（若含「書名/」則去除書名與斜線；未附##時留空）","status":"ok|fixed|uncertain","note":"fixed時簡述修正原因；uncertain時簡述存疑之處，並一併簡述確定誤譯處（若有）；ok留空","translation":"status為fixed時填修正後完整白話；ok或uncertain時留空"}
<<<JSONL_END>>>
