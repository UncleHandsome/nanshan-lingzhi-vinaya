# -*- coding: utf-8 -*-
"""零成本品管掃描：引號白話、目錄膨脹、異體字與網址殘留。

用法：
  python -X utf8 _src/qc_scan.py --materials 測試/實驗11/_材料 --finals 測試/C版11
"""
import argparse
import io
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
BAD_VAR = {'鉢': '缽'}
HAN = re.compile(r'[\u4e00-\u9fff]')

def load_material(key, d):
    p = os.path.join(d, key + '.md')
    if not os.path.exists(p):
        return '', []
    t = io.open(p, encoding='utf-8').read()
    srcs = re.findall(r'■ (?:疏文|記文|鈔文|律文|註文|序文)（原文）(?:\[\d+\])?\s*\n+(.+?)(?=\n+■ |\n+【(?:後文背景|待審譯文|裁決分歧參考|目前譯文|分段要求)|\Z)', t, re.S)
    return t, [s.strip() for s in srcs]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--materials', required=True)
    ap.add_argument('--finals', required=True)
    args = ap.parse_args()

    md = os.path.join(B, args.materials.replace('/', os.sep))
    fd = os.path.join(B, args.finals.replace('/', os.sep))
    keys = sorted(f[:-4] for f in os.listdir(fd)
                  if f.endswith('.txt') and not f.startswith('_'))

    rows = []
    for k in keys:
        _, srcs = load_material(k, md)
        src = ''.join(srcs)
        out = io.open(os.path.join(fd, k + '.txt'), encoding='utf-8').read()

        issues = []
        # 2) 短文膨脹
        sh = len(HAN.findall(src))
        oh = len(HAN.findall(out))
        if sh >= 10 and oh < sh * 0.4:
            issues.append('嚴重縮水（疑漏譯）')
        if 10 <= sh <= 75 and oh > sh * 2.4:
            issues.append('短文膨脹 %d→%d 字' % (sh, oh))

        # 3) 殘留
        if re.search(r'〔[^〕]*(?:據|按|考|校|他本|一本|補[：:])[^〕]*〕', out) or re.search(r'〔疑作[^〕]{1,10}(?:據|卷|頁)', out):
            issues.append('〔〕內疑含校勘按語')
        if 'PASS_A_KEEP_A' in out:
            issues.append('殘留 PASS_A 標記')
        if re.search(r'(?:local_search|web_search|web_fetch)\s*\(', out):
            issues.append('殘留工具呼叫字面')
        if out.count('「') != out.count('」'):
            issues.append('引號未閉合')
        for _bad in ('达', '没', '时', '精准', '颗', '过', '与', '现', '实', '际', '种', '样', '动', '学', '觉', '见', '观', '识', '论', '证', '众', '问', '这', '为', '应', '经', '说', '义', '体', '归', '无', '过', '还', '对', '发', '个', '们', '么', '与', '从', '来', '现', '实', '际', '种', '样', '动', '学', '觉', '见', '观', '识', '论', '证'):
            if _bad in out:
                issues.append('殘留簡體字')
                break
        for _a, _b, _n in (('「', '」', '「」'), ('『', '』', '『』'),
                            ('（', '）', '（）'), ('《', '》', '《》'), ('〔', '〕', '〔〕')):
            if out.count(_a) != out.count(_b):
                issues.append(_n + ' 未成對')
        if 'http' in out:
            issues.append('殘留網址')
        _out_noquote = re.sub(r'[「『][^」』]*[」』]', '', out)
        for bad, good in BAD_VAR.items():
            if bad in _out_noquote:
                issues.append('異體字 %s' % bad)
        _labs = re.findall(r'(?m)^【(疏文|記文|鈔文|律文|註文|序文)】', out)
        if any(_labs.count(x) > 1 for x in set(_labs)):
            issues.append('殘留欄位標籤')

        rows.append((k, issues))

    print('%-4s %s' % ('組', '檢查結果'))
    n_bad = 0
    for k, iss in rows:
        if iss:
            n_bad += 1
            print('%-4s ⚠ %s' % (k, '；'.join(iss)))
        else:
            print('%-4s ✅' % k)
    print('\n需人工複核：%d／%d 組' % (n_bad, len(rows)))


if __name__ == '__main__':
    main()
