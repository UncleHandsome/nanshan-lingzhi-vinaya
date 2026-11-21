# 對話材料 #0880

- event: assistant/message
- seq: 111866
- time: 1795064599658

---

Now tests:
1. judge mother json + ordering: create fixture src material with mother, judge requires blind replies (a) and b='out'. Build minimal:
- src dir with k1.md/json (units, mother, post, ex), 回覆? judge reads a from `_read_side(adir,key,out)` where adir maybe src? args --a can be 'out'? If --a out then reads src material's 現譯? Simpler run with --a out --b out? Then both from md? _read_side(None,...) maybe from src md. Let's inspect _read_side? Might be complex.
Alternative unit test: check mk_judge write_json includes mother by running with --a out --b out on fixture and reading output json. Try.

2. pack pending edge: fixture p3: label once `【疏文】\n[1] 疏1\n[2] 疏2\n【記文】記2?` Hard; simpler test the "last label mid-block" scenario:
```
【疏文】
[1] 疏1
[2] 疏文二
【記文】記文二
[3] 記文三
```
Expected b1=疏1, b2=疏文二+記文二, b3=記文三 (pending from last label 記文).
Run split fixture.

3. revise material no 初審簡核: rerun earlier fixture (deleted) — rebuild quick and check section absent, evidence present.

4. STYLE quote text / REVISE 4 no 篇題.

5. norm doc listing clarification (no 於).

Run tests 1 (judge fixture), 2 (pack fixture), 3 (revise fixture). Let's build script for judge:
- src dir with k1.md containing 本次待審單元? mk_judge expects material md with units; it reads t for ex and parts. It uses `_read_side(adir,key,out)` for 甲 and `_read_side(bdir,...)`; if --a out → reads from md? Look at _read_side definition quickly.