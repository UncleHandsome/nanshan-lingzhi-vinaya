# -*- coding: utf-8 -*-
"""自訂提示詞平行校對：把指定條目用给定提示詞送千問，輸出「輸入＋結果」合檔。

复用 run_3k_review 的 API 設定（qwk2／qwen4-max／xhigh／Responses API web_search＋web_extractor）。

用法：
  # 通用模板＋按書代入（建議）
  python -X utf8 _src/review_entries.py --book zhichi --entries a.md b.md --outdir out
  # 自訂提示詞
  python -X utf8 _src/review_entries.py --prompt 提示詞.md --folder 抽樣_三主題_20261124 --outdir out

條目檔若帶材料註解頭（<!-- ... -->）會自動移除；白話重複【標籤】會去重。
每筆獨立重试 3 次；單筆失敗不影響其他筆。
"""
import argparse
import glob
import io
import os
import re
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(__file__))
import run_3k_review as R
import book_prompt

QUOTA = threading.Event()


def prep(path):
    t = io.open(path, encoding='utf-8').read()
    t = re.sub(r'^<!--.*?-->\s*', '', t, flags=re.S)
    t = re.sub(r'(【[^】]{1,4}】)\n\1', r'\1', t)
    return t.strip()


def is_quota(code, msg):
    low = (msg or '').lower()
    return code in ('401', '402', 'insufficient_quota') or 'quota' in low or 'insufficient' in low


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--book', choices=list(book_prompt.PROFILES),
                    help='按書代入通用模板（book_id／authority／genre_rules）')
    ap.add_argument('--prompt', help='自訂提示詞檔（與 --book 二選一）')
    ap.add_argument('--entries', nargs='*')
    ap.add_argument('--folder')
    ap.add_argument('--outdir', required=True)
    ap.add_argument('--workers', type=int, default=4)
    a = ap.parse_args()
    if not a.book and not a.prompt:
        ap.error('--book 或 --prompt 至少一個')
    book_name = None
    if a.book:
        header = book_prompt.render_prompt(a.book) + '\n'
        book_name = book_prompt.PROFILES[a.book]['name']
    else:
        header = io.open(a.prompt, encoding='utf-8').read().rstrip() + '\n\n'
    files = list(a.entries or [])
    if a.folder:
        files += sorted(p for p in glob.glob(os.path.join(a.folder, '*.md'))
                        if '輸入與結果' not in p and not os.path.basename(p).startswith('_'))
    os.makedirs(a.outdir, exist_ok=True)
    key = io.open(R.KEY_FILE, encoding='utf-8-sig').read().strip()
    meta = '模型：%s｜xhigh｜Responses API web_search＋web_extractor｜金鑰 qwk2' % R.MODEL
    if book_name:
        meta += '｜書別：%s（%s）' % (book_name, a.book)

    def check_book(entry):
        """--book 模式下確認條目標題屬於該書，避免 book_id 誤標。"""
        if not book_name:
            return True
        for ln in entry.splitlines():
            if ln.startswith('## '):
                return book_name in ln
        return False

    def run(path):
        entry = prep(path)
        inp = header + entry + '\n'
        stem = re.sub(r'^\d+_', '', os.path.basename(path)[:-3])
        dst = os.path.join(a.outdir, stem + '_輸入與結果.md')
        if not check_book(entry):
            io.open(dst, 'w', encoding='utf-8', newline='\n').write(
                '# %s 白話校對（千問）\n\n%s\n\n---\n\n## 輸入\n\n%s\n\n'
                '---\n\n## 千問結果\n\n（跳過：條目標題不屬於《%s》，'
                '避免 book_id 誤標）\n' % (stem, meta, inp, book_name))
            return dst, 0, 'skip-book'
        last = ''
        for attempt in range(3):
            if QUOTA.is_set():
                last = 'quota-stop'
                break
            try:
                out = R.call_qwen(inp, key)
                body = ('# %s 白話校對（千問）\n\n%s\n\n---\n\n## 輸入\n\n' % (stem, meta)) \
                    + inp + '\n\n---\n\n## 千問結果\n\n' + out.strip() + '\n'
                io.open(dst, 'w', encoding='utf-8', newline='\n').write(body)
                return dst, len(out), 'ok'
            except R.QwenStreamError as e:
                last = '%s: %s' % (e.code, e.message[:120])
                if is_quota(e.code, e.message):
                    QUOTA.set()
                    break
                time.sleep(8 * (attempt + 1))
            except Exception as e:
                last = type(e).__name__ + ': ' + str(e)[:120]
                time.sleep(8 * (attempt + 1))
        body = ('# %s 白話校對（千問）\n\n%s\n\n---\n\n## 輸入\n\n' % (stem, meta)) \
            + inp + '\n\n---\n\n## 千問結果\n\n（呼叫失敗：%s）\n' % last
        io.open(dst, 'w', encoding='utf-8', newline='\n').write(body)
        return dst, 0, 'fail ' + last

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(run, p): p for p in files}
        for f in as_completed(futs):
            dst, n, st = f.result()
            print(st, os.path.basename(dst), 'result_len', n, flush=True)


if __name__ == '__main__':
    main()
