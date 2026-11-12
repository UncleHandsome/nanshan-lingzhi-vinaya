# -*- coding: utf-8 -*-
"""由 _zx2_log 產生 說明_r2_1048.md 與存疑段。"""
import os, sys, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2a_lib as L

HERE = os.path.dirname(os.path.abspath(__file__))
LOGD = os.path.join(HERE, '_zx2_log')
OUT = os.path.join(HERE, '說明_r2_1048.md')
DOUBT = os.path.join(L.ROOT, '存疑材料', 'r2_存疑', '資持記.md')

logs = []
for fn in sorted(os.listdir(LOGD)):
    if fn.startswith('log_'):
        logs.append(json.load(open(os.path.join(LOGD, fn), encoding='utf-8')))
logs.sort(key=lambda d: d['n'])

per, tot_edits, segs_all, vk = [], 0, set(), collections.Counter()
chunk_stat = collections.OrderedDict()
for d in logs:
    n = d['n']
    eds = d['edits']
    vs = d.get('verdicts', [])
    ch = collections.OrderedDict()
    for e in eds:
        ch.setdefault((e['book'], e['chunk']), set()).add(e['seg'])
    nseg = sum(len(v) for v in ch.values())
    kc = collections.Counter(v['kind'] for v in vs)
    for k, c in kc.items():
        vk[k] += c
    tot_edits += len(eds)
    for (book, chunk), ss in ch.items():
        segs_all |= set((book, chunk, s) for s in ss)
        st = chunk_stat.setdefault((book, chunk), dict(segs=set(), edits=0))
        st['segs'] |= ss
        st['edits'] += len([e for e in eds if e['chunk'] == chunk])
    rng = '；'.join('%s#%d-%d' % (c, min(s), max(s)) for (b, c), s in ch.items()) or '—'
    per.append((n, rng, len(eds), nseg, len(vs), kc.get('誤報', 0), kc.get('存疑', 0)))

nfiles = len(logs)
last = per[-1][0] if per else 1047
nv = sum(p[4] for p in per)
segs = len(segs_all)

L1 = []
w = L1.append
w('# r2 資持記 resp_1048–1180 校閱說明（本輪做到第 %d 檔）' % last)
w('')
w('材料：`校閱_10K/校閱_1048.txt`–`校閱_1180.txt`；回應：`batch_qwen/r2/resp_1048.txt`–`resp_1180.txt`。')
w('本輪處理範圍為 1048–%d；`resp_1065` 檔在 `batch_qwen/r2` 中不存在（材料仍在），未處理亦未登記 done。' % last)
w('做法：每檔先讀回應，逐條判定「真錯／已修／誤報（潤飾、增註、科判誤解、引文查無、要求改回已修）／存疑」；真錯只改問題處，其餘逐字照抄。每筆 edit 由材料 seq 自動解析 book/chunk/seg，套用前驗證 old 在該段恰出現一次、行尾與段數不變。')
w('')
w('## 一、本輪進度')
w('')
w('**處理 %d 檔（做到第 %d 檔）**，改 %d 段、%d 處，否決 %d 條，存疑 %d 條。' % (
    nfiles, last, segs, tot_edits, vk.get('誤報', 0), vk.get('存疑', 0)))
w('')
w('| 項目 | 數量 |')
w('|---|---|')
w('| 處理檔數 | %d（1048–%d，缺 1065） |' % (nfiles, last))
w('| 讀完意見 | %d 條 |' % nv)
w('| 改動段數 | %d 段 |' % segs)
w('| 改動處數 | %d 處 |' % tot_edits)
w('| 否決（誤報／潤飾／增註／已修） | %d 條 |' % vk.get('誤報', 0))
w('| 存疑 | %d 條 |' % vk.get('存疑', 0))
w('')
w('## 二、逐 chunk 表')
w('')
w('| 書/chunk | 段範圍 | 改動處 |')
w('|---|---|---|')
for (book, chunk), st in chunk_stat.items():
    ss = sorted(st['segs'])
    w('| %s/%s | %d–%d（%d 段） | %d |' % (book, chunk, ss[0], ss[-1], len(ss), st['edits']))
w('')
w('## 三、逐檔表（1048–%d）' % last)
w('')
w('| 檔 | 材料段 | 意見 | 改段 | 改處 | 否決 | 存疑 |')
w('|---|---|---|---|---|---|---|')
for p in per:
    w('| %d | %s | %d | %d | %d | %d | %d |' % (p[0], p[1], p[4], p[3], p[2], p[5], p[6]))
w('')
w('## 四、主要修正類型')
w('')
w('1. **科判語讀成實詞**：1051「緣起中」→「在因緣生起中」、1055「便下」→「既然如此」、1064「故下／準下」→「從…開始」、1063「標中」→「在標題中」、1061「列篇中」→「在列出的篇章中」、1059「僧下」→「僧伽以下」。一律改為「『X』字以下」「X 一科中」。')
w('2. **律學專名失真**：1048 六夜＝摩那埵（非別住）、1051 五人法＝五人僧作法、1052 差法含簡德與正差（非羯磨法）、1054 反治＝降等治能舉之人、戒分、緣法二種、1057 七條大衣＝七條衣與大衣、1058 下二衣、1059 輕物、對首／心念、1062 作犯止犯、1064 四墮＝四波羅夷、墮負、1068 止離＝止持、獨頭偷蘭、1069 捨罪、得上＝上文。')
w('3. **書名**：1063／1066／1067「了論」逕題《戒了論》《戒了論疏》，一律作《明了論》《明了論疏》；1054「戒疏說」改「疏中說」（單稱疏指《業疏》）。')
w('4. **引文與解釋混淆**：1048 夾注誤在引號內、1068「舊注」與元照案語圈在同一括注、1058「合牒」譯「全體宣讀」、1064「合證」譯「合當作為證明」。')
w('5. **增譯與無據形容**：1050 頑固、1054 儀軌／極致、1057 醫王／生命可以挽救、1066 體質、1068 破壞／偏頗。')
w('6. **數目與程序**：1048 七日七夜（非七加七）、1051 十日在（定點非區間）、1059 八提舍尼、1060 八九二時＝時與非時、1067 十三根本罪。')
w('7. **錯字**：1050 憇慢→憍慢、1051 滅檳→滅擯。')
w('')
w('## 五、否決（誤報）分類')
w('')
w('| 類別 | 說明與例 |')
w('|---|---|')
w('| 只是潤飾／語感 | 1048 人物稱名統一、1053「古人說」、1058「破例開許」、1062「二乘八」 |')
w('| 增註建議（不改正文） | 1050 處通二界、1056 五德、1057 癊覆、1064 針鼻 |')
w('| 科判／義解尚待核 | 1055「四事」、1066「四事供養」、1063「示單複」 |')
w('| 已修或無據 | 1051「罪犯」已作「所犯」、1052「經文→本宗」無據 |')
w('')
w('## 六、段號對位')
w('')
w('每筆 edit 均由材料標籤解析 book/chunk/seg，不以回應中的序號直接定位；套用前逐筆驗證 old 在該段恰出現一次。期間 1068、1069 各有 1 筆因回應標號與材料 seq 偏移而在 COUNT 檢核現形（1069 將 #5 的內容標作 0005，實對 seq3），均已改回正確段號後套用。')
w('')
w('## 七、驗證與留存')
w('')
w('- 段數與行尾：各 chunk 套用後段數不變、行尾仍為 CRLF（`_zx2_check.py` 以 `_m3` 備份比對）。')
w('- 備份：`歸檔/r2修正前/資持記/<chunk>_m3.txt`（本輪首次改動前快照，不覆蓋前手 `_m2`）。')
w('- 逐檔紀錄：`AI語譯/_work/review/_zx2_log/log_1048.json`–`log_%d.json`；`batch_qwen/r2_done.txt` 已逐檔追加。' % last)
w('- 工具：`_zx2_dg.py`（意見摘要）、`_zx2_view.py`（段檢視）、`_zx2_apply.py`（套用與 m3 備份）、`_zx2_check.py`（段數行尾比對）、`_zx2_report.py`（本說明）。')
w('')
w('## 八、未完成與待辦')
w('')
w('- `resp_1065` 在 `batch_qwen/r2` 中不存在（材料 `校閱_1065.txt` 仍在），未處理、未登記 done。')
w('- %d 檔之後（%d–1180）尚未處理；`resp_1181` 以後依指示不碰。' % (last, last + 1))
w('- 存疑 %d 條已寫入 `存疑材料/r2_存疑/資持記.md`（`<!-- r2 1048 -->` 段）。' % vk.get('存疑', 0))
w('')

open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(L1))
print('wrote', OUT)
print('files', nfiles, 'edits', tot_edits, 'segs', segs, 'verdicts', nv, 'kinds', dict(vk))

# 存疑段
rows = []
for d in logs:
    n = d['n']
    recs = {r['seq']: r for r in L.parse_review(n)}
    for v in d.get('verdicts', []):
        if v['kind'] != '存疑':
            continue
        r = recs.get(v.get('seq'))
        loc = ('%s#%d' % (r['chunk'], r['seg'])) if r else ''
        rows.append('**%d-%04d（%s）**：%s' % (n, v.get('seq', 0), loc, v.get('reason', '')))
if rows:
    sec = ['', '## r2 1048–%d（本輪新增 %d 條）' % (last, len(rows)), '']
    sec += ['%d. %s' % (i + 1, s) for i, s in enumerate(rows)]
    sec += ['']
    if os.path.exists(DOUBT):
        s = open(DOUBT, encoding='utf-8').read()
        a = s.find('<!-- r2 1048 start -->')
        b = s.find('<!-- r2 1048 end -->')
        if a >= 0 and b > a:
            s = s[:a] + '<!-- r2 1048 start -->\n' + '\n'.join(sec) + '\n<!-- r2 1048 end -->\n' + s[b + len('<!-- r2 1048 end -->'):]
        else:
            s += '<!-- r2 1048 start -->\n' + '\n'.join(sec) + '\n<!-- r2 1048 end -->\n'
    else:
        s = '# 資持記存疑\n<!-- r2 1048 start -->\n' + '\n'.join(sec) + '\n<!-- r2 1048 end -->\n'
    open(DOUBT, 'w', encoding='utf-8', newline='\n').write(s)
    print('doubts', len(rows))
