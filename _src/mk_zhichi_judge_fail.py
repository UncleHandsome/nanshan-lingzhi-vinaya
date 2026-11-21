# -*- coding: utf-8 -*-
import io, os, json
B=r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
root=os.path.join(B,'測試','重譯','資持記')
keys=['24','64','202','1000','1205','1500','1770','2045','2103','2133','2469','2497','2696','2783','3166','3174','3376','3472','3483']
idx=json.load(io.open(os.path.join(root,'_打包審核','索引_pack.json'),encoding='utf-8'))
pk={m:pack for pack,ms in idx.items() for m in ms}
lines=['# 資持記 裁決失敗清單','','```text','這些回覆沒有【結論】／【修正後的譯文】，是研究中途回覆，不是正式裁決。','```','',
       '| key | 回覆字數 | pack | 回覆開頭 |','|:--|--:|:--|:--|']
for k in keys:
    p=os.path.join(root,'_裁決','回覆',k+'_回.txt')
    t=io.open(p,encoding='utf-8').read().strip() if os.path.exists(p) else ''
    lines.append('| %s | %d | %s | %s |'%(k,len(t),pk.get(k,'?'),t[:50].replace('|','｜').replace('\n',' ')))
lines += ['','## 重跑清單','','```text'] + keys + ['```','']
io.open(os.path.join(B,'重作材料_長段','資持記_裁決失敗19.md'),'w',encoding='utf-8').write('\n'.join(lines))
io.open(os.path.join(B,'重作材料_長段','資持記_裁決失敗19_keys.txt'),'w',encoding='utf-8').write('\n'.join(keys)+'\n')
print('ok')
