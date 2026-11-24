# -*- coding: utf-8 -*-
"""自訂提示詞平行校對：把指定條目用给定提示詞送千問，輸出「輸入＋結果」合檔。

复用 run_3k_review 的 API 設定（qwk2／qwen4-max-preview／xhigh／search_strategy=max）。

用法：
  python -X utf8 _src/review_entries.py --prompt 提示詞.md --entries a.md b.md --outdir 輸出目錄 [--workers 4]
  python -X utf8 _src/review_entries.py --prompt 提示詞.md --folder 抽樣_三主題_20261124 --outdir out

條目檔若帶材料註解頭（<!-- ... -->）會自動移除；白話重複【標籤】會去重。
"""
import argparse
import glob
import io
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(__file__))
import run_3k_review as R


def prep(path):
    t = io.open(path, encoding='utf-8').read()
    t = re.sub(r'^<!--.*?-->\s*', '', t, flags=re.S)
    t = re.sub(r'(【[^】]{1,4}】)\n\1', r'\1', t)
    return t.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--prompt', required=True)
    ap.add_argument('--entries', nargs='*')
    ap.add_argument('--folder')
    ap.add_argument('--outdir', required=True)
    ap.add_argument('--workers', type=int, default=4)
    a = ap.parse_args()
    header = io.open(a.prompt, encoding='utf-8').read().rstrip() + '\n\n'
    files = list(a.entries or [])
    if a.folder:
        files += sorted(p for p in glob.glob(os.path.join(a.folder, '*.md'))
                        if '輸入與結果' not in p and not os.path.basename(p).startswith('_'))
    os.makedirs(a.outdir, exist_ok=True)
    key = io.open(R.KEY_FILE, encoding='utf-8-sig').read().strip()

    def run(path):
        entry = prep(path)
        inp = header + entry + '\n'
        out = R.call_qwen(inp, key)
        stem = os.path.basename(path)[:-3]
        stem = re.sub(r'^\d+_', '', stem)
        dst = os.path.join(a.outdir, stem + '_輸入與結果.md')
        body = ('# %s 白話校對（千問）\n\n模型：%s｜xhigh｜search_strategy=max｜金鑰 qwk2\n\n'
                '---\n\n## 輸入\n\n' % (stem, R.MODEL)) + inp + '\n\n---\n\n## 千問結果\n\n' + out.strip() + '\n'
        io.open(dst, 'w', encoding='utf-8', newline='\n').write(body)
        return dst, len(out)

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for dst, n in ex.map(run, files):
            print('done', dst, 'result_len', n, flush=True)


if __name__ == '__main__':
    main()
