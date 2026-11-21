# 對話材料 #1152

- event: assistant/message
- seq: 131528
- time: 1795240871656

---

戒疏、業疏已改成和合編本一樣的做法：

- 不是整組 pair 上色
- 是**只對來源欄 `<div class="o">` 上色**
- 白話欄 `<div class="t">` 保持黑色

現在 class 是：

```html
<div class="pair s">
  <div class="o shu">【疏文】原文</div>
  <div class="t">【疏文】白話</div>
</div>

<div class="pair j">
  <div class="o ji">【記文】原文</div>
  <div class="t">【記文】白話</div>
</div>
```

另外：

- 註文：`o zhu`
- 律文：`o lv`
- 序文：`o xu`

已套用：

| 書 | 疏文 | 記文 |
|:--|--:|--:|
| 戒疏 | 3,224 | 3,112 |
| 業疏 | 2,503 | 2,309 |

- commit：`103e590`
- 推送：`0da2db8..103e590`

重新整理或 Ctrl+F5 後，顏色應該只出現在原文欄，白話欄不再上色。