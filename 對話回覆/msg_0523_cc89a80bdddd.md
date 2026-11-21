# 對話材料 #0523

- event: assistant/message
- seq: 79471
- time: 1794788867107

---

do_split `mat` is path as given (likely absolute or relative CWD project). Helper uses os.path.join(mat, ok_key) fine if mat absolute; CLI passes relative 測試/... with cwd B? Test with absolute.

Build synthetic offline test:
- dir /tmp test/_pk: 索引_pack.json {"p0001":["a1","a2","a3"]}
- p0001.md with 3 groups each ■ 疏文（譯本甲）[i] text 甲i
- 回覆/p0001_回.txt reply with REVISED and only [1] changed, 第2欄 [1] line, 第3欄 【疏文】\n[1] 改1
- run pack_judge --mode split --replies 回覆 --mat test/_pk (absolute)
- check _拆回/回覆/a2_回.txt contains 甲2 and REVISED.

Run.