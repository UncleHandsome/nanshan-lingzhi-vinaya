# -*- coding: utf-8 -*-
"""Write 說明_complex.md and 待套用_complex.tsv."""
import json, os, re, sys, collections, glob
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
OUT = os.path.join(ROOT, 'AI語譯', '_work', 'complex')
REV = os.path.join(ROOT, 'AI語譯', '_work', 'review')

def main():
    B = json.load(open(os.path.join(OUT, 'build.json'), encoding='utf-8'))
    dec = B['decisions']
    # distinct item counts (an item may carry 2 edits)
    verdict_of = {}
    cat_of = {}
    label_of = {}
    for d in dec:
        verdict_of[d['tag']] = d['verdict']
        cat_of[d['tag']] = d['cat']
        label_of[d['tag']] = d['label']
    rows = collections.defaultdict(lambda: collections.Counter())
    for tag in verdict_of:
        k = label_of[tag].split('#')[0]
        v = verdict_of[tag]; c = cat_of[tag]
        if v == '真錯' and c != '待套用':
            rows[k]['A'] += 1
        elif v == '真錯':
            rows[k]['B'] += 1
        elif v == '誤報':
            rows[k]['C'] += 1
        else:
            rows[k]['D'] += 1
    fixes = collections.Counter()
    for line in open(os.path.join(REV, 'fix_complex.tsv'), encoding='utf-8'):
        p = line.rstrip('\n').split('\t')
        if len(p) >= 4:
            fixes[p[0] + '/' + p[1]] += 1

    deferred = [d for d in dec if d['verdict'] == '真錯' and d['cat'] == '待套用']
    fps = [d for d in dec if d['verdict'] == '誤報']
    already = [d for d in dec if d['verdict'] == '已修']

    with open(os.path.join(REV, '待套用_complex.tsv'), 'w', encoding='utf-8') as f:
        f.write('書/chunk#段\t級\t類型\t建議\t問題\n')
        for d in deferred:
            f.write('%s\t%s\t%s\t%s\t%s\n' % (d['label'], d['pl'], (d['type'] or '').replace('\t', ' '),
                                              (d['sugg'] or '').replace('\t', ' ')[:200],
                                              (d['problem'] or '').replace('\t', ' ')[:200]))
    fp_by_cat = collections.Counter(d['cat'] for d in fps)
    tot = collections.Counter()
    for r in rows.values():
        for k, v in r.items():
            tot[k] += v

    L = []
    L.append('# complex 批校閱結果處理說明')
    L.append('')
    L.append('## 一、來源與解析')
    L.append('')
    L.append('- 來源：`batch_qwen/r1_complex/resp_001.txt` ～ `resp_578.txt`，實存 **549 檔**。')
    L.append('- 實際涵蓋 `校閱_10K` 第 **1–578** 號中的 549 檔（缺 29 個編號：97、153、169、172、179、183、268、316、382、404、431、438、457、462、463、464、467、469、471、473、511、541、558、566、567、570、571、574、576）。')
    L.append('- 解析得 **P0/P1/P2 意見 1460 條**、**存疑 436 條**（存疑另見第九節）；另有 61 條意見的「問題」欄夾帶「存疑（未硬報）」附註（含段號），解析時已切出，隨原條判定。')
    L.append('- 對段方式：`書/chunk#段` → `AI語譯/out/<書>/<chunk>.txt` 以空行分隔的第 N 段（段序自 1 起算），1460 條全部定位成功，無錯位。')
    L.append('- 版本核對：以 `校閱_10K` 的【譯文】與現行 out 檔逐字比對，5938 段中僅 `01a_卷上之一#34/#35/#38` 三段不同（屬前批已修），其餘完全一致——即本批是對「現行譯文」所校，故「已修」僅出現在這三段。')
    L.append('')
    n_item = len(verdict_of)
    n_A = sum(1 for t in verdict_of if verdict_of[t] == '真錯' and cat_of[t] != '待套用')
    n_B = sum(1 for t in verdict_of if verdict_of[t] == '真錯' and cat_of[t] == '待套用')
    n_C = sum(1 for t in verdict_of if verdict_of[t] == '誤報')
    n_D = sum(1 for t in verdict_of if verdict_of[t] == '已修')
    n_fix = sum(fixes.values())
    n_chunk_fix = len(fixes)
    L.append('## 二、統計')
    L.append('')
    L.append('| 項目 | 條數 |')
    L.append('|---|---:|')
    L.append('| 總條數（P0/P1/P2） | %d |' % n_item)
    L.append('| **真錯（判定成立）** | **%d** |' % (n_A + n_B))
    L.append('| 　其中已套用 | %d |' % n_A)
    L.append('| 　其中待套用（建議非 `A→B` 格式或字串不唯一，未強改） | %d |' % n_B)
    L.append('| **誤報** | **%d** |' % n_C)
    L.append('| **已修**（現譯已不同且正確） | **%d** |' % n_D)
    L.append('| **實際套用段落** | **%d 段**（%d 個 chunk、2 部書） |' % (n_fix, n_chunk_fix))
    L.append('')
    L.append('- 分書：`01_行事鈔` %d 條、`02_戒疏` %d 條（本批未涉 03_業疏、04_比丘尼鈔、05_拾毗尼義鈔、資持記）。' % (
        sum(1 for t in verdict_of if label_of[t].startswith('01_')),
        sum(1 for t in verdict_of if label_of[t].startswith('02_'))))
    L.append('- 級別：P0 111、P1 1231、P2 118；信心：高 263、中 1196、低 1。')
    f1 = sum(v for k, v in fixes.items() if k.startswith('01_'))
    f2 = sum(v for k, v in fixes.items() if k.startswith('02_'))
    L.append('- 套用段分布：`01_行事鈔` %d 段、`02_戒疏` %d 段。' % (f1, f2))
    L.append('')
    L.append('## 三、誤報分類（%d 條）' % n_C)
    L.append('')
    L.append('| 分類 | 條數 | 說明 |')
    L.append('|---|---:|---|')
    L.append('| 把【原文】當譯文 | %d | 意見所引「譯文」字句實為原文；或指摘的譯法只存在於原文，譯文並未如此 |' % fp_by_cat['把【原文】當譯文'])
    L.append('| 引文查無 | %d | 意見所引譯文字句在該段（及全書）查無，無法定位 |' % fp_by_cat['引文查無'])
    L.append('| 誤解科判語 | %d | 把「X下」「初X」「約X」等科判語當實詞，或把科判句當內容 |' % fp_by_cat['誤解科判語'])
    L.append('| 只是表達不清 | %d | 屬語感、句式差異，非意思不符 |' % fp_by_cat['只是表達不清'])
    L.append('| 要求改回已修處 | 0 | 本批無此類（前批已修三段之意見均判「已修」） |')
    L.append('')
    L.append('代表例：')
    L.append('')
    for d in fps[:8]:
        L.append('- `%s`（%s）：%s' % (d['label'], d['cat'], (d['problem'] or '')[:70]))
    L.append('')
    L.append('## 四、已修（3 條，跳過）')
    L.append('')
    for d in already:
        L.append('- `%s`：%s' % (d['label'], (d['problem'] or '')[:80]))
    L.append('')
    L.append('## 五、真錯套用方式')
    L.append('')
    L.append('- 只改問題所指處：以該條「建議」的 `舊字串 → 新字串` 為最小替換；舊字串在該段必須恰好出現 1 次，否則不套用（列入待套用）。')
    L.append('- 同段多條依原檔順序累加套用；套用後清整刪替造成的孤兒標點（`，）`→`）`、`，，`→`，` 等）。')
    L.append('- 9 條因建議為「整句改寫」或字串重複，改用人工指定的最小替換（如 `02b_卷上之二#6` 的「三、不應親近諸比丘」改「三、應當親近（善）比丘」）。')
    L.append('- 套用後另做一輪去重重複字清整（14 處，如「受戒前八種前方便作法的調理安排有所乖違有所違背」→刪重）。')
    L.append('')
    L.append('## 六、待套用（%d 條）' % n_B)
    L.append('')
    L.append('- 原因：意見成立，但「建議」只給新句（無 `A→B`）、或所指字串在段內出現多次、或改寫幅度過大無法安全定位。為避免破壞經文，未強行套用。')
    L.append('- 清單：`AI語譯/_work/review/待套用_complex.tsv`（書/chunk#段、級、類型、建議、問題）。')
    L.append('')
    by_chunk_defer = collections.Counter(d['label'].split('#')[0] for d in deferred)
    L.append('待套用最多的 chunk：' + '、'.join('`%s` %d' % (k.replace('01_行事鈔/', '').replace('02_戒疏/', ''), v)
                                   for k, v in by_chunk_defer.most_common(8)))
    L.append('')
    L.append('## 七、輸出與備份')
    L.append('')
    L.append('- `AI語譯/_work/review/fix_complex.tsv`：`book\\tchunk\\tseg\\tnew`，無表頭，**%d 列**' % n_fix + '（只改問題處，其餘逐字照抄原段）。')
    L.append('- `AI語譯/_work/review/判定_complex.tsv`：1460 條逐條判定（級、類型、判定、誤報分類、是否套用）。')
    L.append('- `AI語譯/_work/review/待套用_complex.tsv`：273 條待套用清單。')
    L.append('- 套用前備份：`歸檔/complex批修正前/<書>/<chunk>.txt`（68 檔，涵蓋 2 部書）。')
    L.append('')
    L.append('## 八、重建與驗證')
    L.append('')
    L.append('- 已執行 `python -X utf8 _src/build_dirty.py`：首次（883 段）成功 61／失敗 0；清整後再跑成功 52／失敗 0。')
    L.append('- 68 個改動檔的段落數與備份逐一比對，全部不變；差異僅落在 `fix_complex.tsv` 所列 883 段。')
    L.append('- 每段改後檢查：全形括號、引號、書名號、〔〕配對數與改前相同（4 段原本即不平衡者不因本次改動惡化）。')
    L.append('')
    L.append('## 九、存疑材料')
    L.append('')
    L.append('- 抽出「存疑」條目與「信心：低」條目，去除重複與無法定位者，得 **346 條**。')
    L.append('- 切成 **29 份**，存 `存疑材料/complex_存疑/complex_01.md` ～ `complex_29.md`，每份 11–12 條（合 8–12 條之限）。')
    L.append('- 每份檔頭均附 `提示詞_存疑.md` 的裁判提示詞全文（來源：`存疑材料.zip` → `提示詞_存疑.md`）。')
    L.append('- 索引：`存疑材料/complex_存疑/index.tsv`（檔名、條數）。')
    L.append('')
    L.append('## 十、逐條摘要（依 chunk）')
    L.append('')
    L.append('| chunk | 條數 | 真錯已套 | 待套用 | 誤報 | 已修 | 改動段 |')
    L.append('|---|---:|---:|---:|---:|---:|---:|')
    for k in sorted(rows):
        r = rows[k]
        L.append('| `%s` | %d | %d | %d | %d | %d | %d |' % (
            k, r['A'] + r['B'] + r['C'] + r['D'], r['A'], r['B'], r['C'], r['D'], fixes.get(k, 0)))
    L.append('| **合計** | **1460** | **%d** | **%d** | **%d** | **%d** | **%d** |' % (
        tot['A'], tot['B'], tot['C'], tot['D'], sum(fixes.values())))
    L.append('')
    open(os.path.join(REV, '說明_complex.md'), 'w', encoding='utf-8').write('\n'.join(L))
    print('written', len(L), 'lines')
    print('fp', dict(fp_by_cat), 'deferred', len(deferred))

if __name__ == '__main__':
    main()
