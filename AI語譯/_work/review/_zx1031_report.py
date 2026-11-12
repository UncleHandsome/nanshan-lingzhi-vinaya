# -*- coding: utf-8 -*-
"""由 _zx1031_log 產生 說明_r2_1031.md（統計表自動，敘述固定）。"""
import os, sys, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _r2a_lib as L

HERE = os.path.dirname(os.path.abspath(__file__))
LOGD = os.path.join(HERE, '_zx1031_log')
OUT = os.path.join(HERE, '說明_r2_1031.md')

logs = []
for fn in sorted(os.listdir(LOGD)):
    if fn.startswith('log_'):
        n = int(fn[4:-5])
        if 1031 <= n <= 1180:
            logs.append(json.load(open(os.path.join(LOGD, fn), encoding='utf-8')))
logs.sort(key=lambda d: d['n'])

per, tot_edits, segs, vk = [], 0, 0, collections.Counter()
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
    segs += nseg
    for (book, chunk), ss in ch.items():
        st = chunk_stat.setdefault((book, chunk), dict(segs=set(), edits=0))
        st['segs'] |= ss
        st['edits'] += sum(1 for e in eds if e['chunk'] == chunk)
    rng = '；'.join('%s#%d-%d' % (c, min(s), max(s)) for (b, c), s in ch.items())
    per.append((n, rng, len(eds), nseg, len(vs), kc.get('真錯', 0), kc.get('誤報', 0), kc.get('存疑', 0)))

nfiles = len(logs)
nv = sum(p[4] for p in per)
last = per[-1][0] if per else 1030

L1 = []
w = L1.append
w('# r2 資持記 resp_1031–1180 校閱說明（本輪做到第 %d 檔）' % last)
w('')
w('材料：`校閱_10K/校閱_1031.txt`–`校閱_1180.txt`；回應：`batch_qwen/r2/resp_1031.txt`–`resp_1180.txt`（其中 resp_1065、resp_1086、resp_1105 三檔缺失，見第八節）。')
w('對應正文：資持記 `05b_上四#20`–`09c_中三上#17`。')
w('做法：每檔逐條讀回應意見，逐條判定「真錯／已修／誤報（潤飾、增註、科判誤解、引文查無、要求改回已修）／存疑」；真錯只改問題處，其餘逐字照抄；套用前以材料 seq 自動解析 book/chunk/seg，並驗證 old 在該段恰出現一次、段數與行尾不變。')
w('')
w('## 一、本輪進度')
w('')
w('**處理 %d 檔（做到第 %d 檔）**，改 %d 段、%d 處，否決 %d 條，存疑 %d 條。' % (
    nfiles, last, segs, tot_edits, vk.get('誤報', 0), vk.get('存疑', 0)))
w('')
w('| 項目 | 數量 |')
w('|---|---|')
w('| 處理檔數 | %d（1031–%d） |' % (nfiles, last))
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
w('## 三、逐檔表（1031–%d）' % last)
w('')
w('| 檔 | 材料段 | 意見 | 改段 | 改處 | 否決 | 存疑 |')
w('|---|---|---|---|---|---|---|')
for p in per:
    w('| %d | %s | %d | %d | %d | %d | %d |' % (p[0], p[1], p[4], p[3], p[2], p[6], p[7]))
w('')
w('## 四、主要修正類型')
w('')
w('1. **科判語讀成實詞／連詞**：1031「對說中」讀成「面對外緣」、1032「開章標列」讀成狀語、「牒釋」漏牒、1035「開章標列」「五中復五」、1036「雖下／然下」讀成「雖然…然而」、1038「問答中」譯「在問答之中」、1044「並下／總下」讀成「以上統統」、1045「離合中三」。一律改為「『X』字以下」「X 一科中」。')
w('2. **律學專名走味**：1031 利己→利養；1032 上座→首座；1033 別眾／別法／心念（一人自說）／隨戒；1034 忘成（忘結安居）≠結界、五利≠財物利養、受日≠七日；1035 定位（時位）≠地位、《了疏》≠戒疏；1036 解界≠解除界限、僧師≠僧導師；1037 前坐＝前安居；1038 攝閏＝計入閏月；1039 反＝相反（四處）、通＝通攝；1041「對念、忘及」名相流失；1046 僧次請≠僧團邀請、受懺＝受他人懺悔。')
w('3. **《疏》＝《羯磨疏》**：1031（#24 疏云）、1032（#35 故疏云）、1033（#40、#42、#43）、1035（#57 疏列三種）。原譯多逕題「戒疏」，一律改「《疏》（《羯磨疏》）」。1033「《了疏》」另指《明了論》之疏。')
w('4. **引文與解釋混為一談**：1034「〔此處為戒疏原文〕」；1042「疾還界內」把元照釋文當引文（應作「即返界」）；1043「牒」誤作「宣讀」（二處）；1044「捨制取聽」主語含糊。')
w('5. **增譯與無據形容**：1031 厲色增「威嚴」、縱令永廢擴為「正法」；1032 嚴寒酷暑；1033 痛斥、位格、無比宏大；1035 極小簡陋、樹神極其憤怒；1036 無端、慈愛、深奧、正宗；1039 摸彩、出資、名下財物；1040 大興土木、明師大德；1041 通權達明、極為深刻圓滿；1046 加持、濟度、廣論、縱容。')
w('6. **數目與程序**：1031 布薩譯「每月」（應半月）；1032 為廣三十九十；1034 受日誤限七日；1035 三時並吉誤作「外出」；1036 前後一日誤作各住一天；1038 閏五月六月漏閏、三時（熱雨寒）誤作春夏冬；1045 一日已去／十六日去無上限。')
w('7. **引文用字**：1035「結業纏」增「身」、「流苦海」改「漂流苦海」；1036「莫放逸」後引號圈入夾注。')
w('')
w('## 五、否決（誤報）分類')
w('')
w('| 類別 | 說明與例 |')
w('|---|---|')
w('| 只是潤飾／語感 | 1031「總括顯示六聚」（諸聚作六聚不誤）、1032「題首／齊略」、1034「本位加註」、1035「後科作最後一科」 |')
w('| 增註建議（不改正文） | 1032「三十九十加註」、1035「二難補註」、1041「園界雙隻加註」、1042「一坐補注」 |')
w('| 科判誤解（意見本身誤讀） | 1033「並結正」、1041「制開義立」、1044「舊記云出古義」 |')
w('| 引文查無／材料體例 | 1032「原文括號未閉合」（材料體例，譯文補足無誤）、1036「敷具統一」（體例建議） |')
w('| 要求改回已修處 | 1033「如法治」（已依律文處理）、1040「院相」（譯文可通） |')
w('')
w('## 六、段號對位')
w('')
w('每筆 edit 均由材料標籤解析出 book/chunk/seg，不以回應中的序號直接定位；套用前逐筆驗證 old 在該段恰出現一次（COUNT 檢核），全數通過後才寫檔。1031–1046 期間共 4 筆因回應誤標段號（1032 將 #32 誤標 0004、1034 將 #51 誤標 0005、1035 將 #55 誤標 0003、1044 將 #2 誤標 0006）而在 COUNT 檢核現形，均已改回正確段號。')
w('')
w('## 七、驗證與留存')
w('')
w('- 段數與行尾：各 chunk 套用後段數不變、行尾仍為 CRLF（`_zx1031_check.py` 以 `_m2` 備份比對）。')
w('- 備份：`歸檔/r2修正前/資持記/<chunk>_m2.txt`（本輪首次改動前快照，不覆蓋前手 `_g`）。')
w('- 逐檔紀錄：`AI語譯/_work/review/_zx1031_log/log_1031.json`–`log_%d.json`；`batch_qwen/r2_done.txt` 已追加 1031-1038、1039-1040、1041-1043 等段。' % last)
w('- 工具：`_zx1031_ws.py`（工作單）、`_zx1031_build.py`（seq→seg 解析與 COUNT 預檢）、`_zx1031_apply.py`（套用與 m2 備份）、`_zx1031_check.py`（段數行尾比對）。')
w('')
w('## 八、未完成與待辦')
w('')
w('- `resp_1065`、`resp_1086`、`resp_1105` 三檔在 `batch_qwen/r2` 中不存在（材料 `校閱_1065/1086/1105.txt` 仍在），該三檔本輪未處理，亦未登記 done。')
w('- %d 檔之後（%d–1180）尚未處理；`resp_1181` 以後依指示不碰。' % (last, last + 1))
w('- 存疑 %d 條已寫入 `存疑材料/r2_存疑/資持記.md`（末節「r2 1031–%d」）。' % (vk.get('存疑', 0), last))
w('')

open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(L1))
print('wrote', OUT)
print('files', nfiles, 'edits', tot_edits, 'segs', segs, 'verdicts', nv, 'kinds', dict(vk))

