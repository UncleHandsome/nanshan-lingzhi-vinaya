# 資持記 pack 審後拆回報告

## 目的

解決 `pack_audit` 整包 FIX 必須整包送修的問題。

做法：審核仍打包，審完立刻依 `[n]` 拆回單段。

## 結果

```text
已審 pack：579
拆回單位：926
PASS：762
FIX：164
```

輸出：

```text
測試/重譯/資持記/_終審_拆回/回覆/<key>_回.txt
```

## 規則

- 整包 PASS：所有成員寫 PASS
- 整包 FIX：只把被 `[n]` 點名的成員寫 FIX
- 未被點名：PASS，不進修訂
- FIX 但有硬傷未標 `[n]`：該包所有成員保留 FIX（安全退路）

## 下一步

只對 164 個 FIX 成員產修訂材料：

```bash
python -X utf8 _src/mk_revise_materials.py \
  --r1 測試/重譯/資持記/_裁決 \
  --audit 測試/重譯/資持記/_終審_拆回 \
  --out 測試/重譯/資持記/_終修_拆回
```

再走 `build_a2.py`：

```bash
python -X utf8 _src/build_a2.py \
  --base 測試/重譯/資持記/_裁決 \
  --audit 測試/重譯/資持記/_終審_拆回 \
  --revise 測試/重譯/資持記/_終修_拆回 \
  --out 測試/重譯/資持記/_定稿_拆回
```

這樣 PASS 段不會被重譯，`_裁決` 的分歧參考也會保留。
