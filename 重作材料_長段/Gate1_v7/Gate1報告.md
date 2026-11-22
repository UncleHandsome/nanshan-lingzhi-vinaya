# Gate1 10 段代表案例（v7）

- 單段、複合鍵；REAUDIT→split→REVISE→VERIFY。
- 候選：`定稿_v2/Gate1_v7/`。

## 結果

```text
FIX 4、PASS 5、異常 1、待跑 0
```

- FIX：`xingshichao__493`、`xingshichao__GAP75`、`yichao__46`、`yichao__GAP23`
- 異常：`yichao__GAP11-25`（缺【分段核驗表】，回覆本身無【結論】，仍需重跑）

## 實際改動

```text
yichao__46        431→427 漢字
yichao__GAP23     1264→1260
xingshichao__493  230→206（QC：疑自加解說括號 1＞0）
xingshichao__GAP75 761→753
```

四筆均 VERIFY OK；`GAP11-25` 未套入。候選 source 不變。

## 成本

```text
REAUDIT 10 回覆：537,429 in／179,359 out
REVISE  4 回覆：163,817／43,623
VERIFY  4 回覆：86,373／5,449
```

耗時約 18:03–18:20（Asia/Taipei）。
