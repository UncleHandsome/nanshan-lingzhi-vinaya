# -*- coding: utf-8 -*-
"""為義鈔等書的段落加上新式標點（只改標點，不動字詞）。

預設處理全部非空行（--min 0），不再跳過 100–500 字的正常段落。
--max 可限制上限，--work／--out 可指定材料與輸出目錄。

用法：
  python -X utf8 _src/mk_punctuate.py --book 義鈔                    # 全部段落產生材料
  python -X utf8 _src/mk_punctuate.py --book 義鈔 --min 100 --max 500 # 只做短段
  python -X utf8 _src/mk_punctuate.py --book 義鈔 --dry-run          # 只統計，不寫檔
  python -X utf8 _src/mk_punctuate.py --book 義鈔 --verify           # 驗證並輸出標點檔
"""
import argparse
import io
import json
import os
import re

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'

BOOKS = {
    '義鈔': dict(src='TXT_分卷/05_拾毗尼義鈔', skip=5, out='TXT_分卷/05_拾毗尼義鈔_標點'),
    '尼鈔': dict(src='TXT_分卷/04_比丘尼鈔', skip=5, out='TXT_分卷/04_比丘尼鈔_標點'),
    '行事鈔': dict(src='TXT_分卷/01_行事鈔', skip=5, out='TXT_分卷/01_行事鈔_標點'),
}

PROMPT = '''你是古籍標點專家。下面是一段未加句讀的漢文佛典原文，請為它加上**新式標點**。

### 規則：
1. **只加標點，不得增、刪、改動任何字詞**（包含異體字、通假字、既有校勘符號〔…〕與缺字方框 □），一字都不能變。
2. 可用標點：，。、；：？！「」『』（）——。
3. 依文義斷句；引文用「」；原文既有的「問」「答」（或「問曰」「答曰」等）後加冒號，絕不可自行增刪「問」「答」「曰」等字；「云」「曰」後得依文義加冒號或逗號；科判層次可用。或；
4. **只輸出加好標點的原文**，不要任何說明、標題或譯文。
5. **你沒有任何工具可用**：只輸出加好標點的正文；不得輸出 tool_call、搜尋指令、程式碼或思考過程；
   必須直接給出加好標點的完整原文，一次寫完。

### 原文（第 {idx} 段）：
{text}
'''

HAN = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff\U00020000-\U0002ebe0]')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--book', required=True)
    ap.add_argument('--min', type=int, default=0,
                    help='最短字數；預設 0，全部非空行都處理（舊版預設 500 會漏掉短段）')
    ap.add_argument('--max', type=int, default=0,
                    help='最長字數；0 表示不限')
    ap.add_argument('--work', default='', help='材料目錄；預設 測試/標點/<book>')
    ap.add_argument('--out', default='', help='輸出目錄；預設由 BOOKS 決定')
    ap.add_argument('--dry-run', action='store_true', help='只統計選取段數，不寫材料')
    ap.add_argument('--allow-empty', action='store_true',
                    help='--verify 時即使 0 段可套用也照樣輸出（預設不寫，避免覆蓋既有句讀）')
    ap.add_argument('--verify', action='store_true')
    args = ap.parse_args()

    spec = BOOKS[args.book]
    sd = os.path.join(B, spec['src'].replace('/', os.sep))
    work = os.path.join(B, (args.work or os.path.join('測試', '標點', args.book)).replace('/', os.sep))
    outdir = os.path.join(B, (args.out or spec['out']).replace('/', os.sep))

    if not args.verify:
        mdir = os.path.join(work, '_材料')
        rdir = os.path.join(mdir, '回覆')
        meta = []
        n = 0
        skipped = 0
        short = 0
        if not args.dry_run:
            os.makedirs(mdir, exist_ok=True)
            for f in os.listdir(mdir):
                fp = os.path.join(mdir, f)
                if os.path.isfile(fp):
                    os.remove(fp)
            os.makedirs(rdir, exist_ok=True)
            for f in os.listdir(rdir):
                os.remove(os.path.join(rdir, f))
        for fn in sorted(os.listdir(sd)):
            if not fn.endswith('.txt'):
                continue
            chunk = fn[:-4]
            lines = [x.strip() for x in io.open(os.path.join(sd, fn), encoding='utf-8',
                                                errors='ignore').read().split('\n')[spec['skip']:] if x.strip()]
            for idx, line in enumerate(lines):
                if len(line) <= args.min:
                    skipped += 1
                    continue
                if args.max and len(line) > args.max:
                    skipped += 1
                    continue
                n += 1
                if 100 <= len(line) <= 500:
                    short += 1
                meta.append(dict(no=n, chunk=chunk, idx=idx, text=line, length=len(line)))
                if not args.dry_run:
                    io.open(os.path.join(mdir, '%03d.md' % n), 'w', encoding='utf-8').write(
                        PROMPT.format(idx=idx + 1, text=line))
        if args.dry_run:
            print('%s：--min %d --max %d 會選 %d 段（其中 100–500 字 %d 段；跳過 %d 段）'
                  % (args.book, args.min, args.max, n, short, skipped))
            return
        json.dump(meta, io.open(os.path.join(work, 'meta.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        print('%s：%d 段待標點（100–500 字 %d 段；跳過 %d 段）→ %s'
              % (args.book, n, short, skipped, work))
        return

    meta = json.load(io.open(os.path.join(work, 'meta.json'), encoding='utf-8'))
    ok = 0
    missing = 0
    rejected = 0
    new_lines = {}
    for m in meta:
        p = os.path.join(work, '_材料', '回覆', '%03d_回.txt' % m['no'])
        if not os.path.exists(p):
            missing += 1
            continue
        out = io.open(p, encoding='utf-8').read().strip()
        a = ''.join(HAN.findall(m['text']))
        b = ''.join(HAN.findall(out))
        if m['text'].count('□') != out.count('□'):
            print('缺字方框數不符：%03d' % m['no'])
            rejected += 1
            continue
        if a != b:
            print('字詞不符：%03d（原 %d 字，回 %d 字）' % (m['no'], len(a), len(b)))
            rejected += 1
            continue
        new_lines[(m['chunk'], m['idx'])] = out
        ok += 1

    if ok == 0 and meta and not args.allow_empty:
        print('沒有任何可套用回覆，未寫入 %s（避免把既有句讀覆蓋成 raw；要強制輸出請加 --allow-empty）'
              % outdir)
        return

    os.makedirs(outdir, exist_ok=True)
    for fn in sorted(os.listdir(sd)):
        if not fn.endswith('.txt'):
            continue
        chunk = fn[:-4]
        raw = io.open(os.path.join(sd, fn), encoding='utf-8', errors='ignore').read()
        source_lines = raw.split('\n')
        # 若輸出檔已存在且正文漢字序列與 raw 相同，以既有句讀為底，只替換本次已驗證的行
        base_lines = source_lines
        op = os.path.join(outdir, fn)
        if os.path.exists(op):
            old = io.open(op, encoding='utf-8', errors='ignore').read().split('\n')
            same_han = (''.join(HAN.findall('\n'.join(old[spec['skip']:]))) ==
                        ''.join(HAN.findall('\n'.join(source_lines[spec['skip']:]))))
            same_n = (sum(1 for x in old[spec['skip']:] if x.strip()) ==
                      sum(1 for x in source_lines[spec['skip']:] if x.strip()))
            if same_han and same_n:
                base_lines = old
        skip = spec['skip']
        head = '\n'.join(base_lines[:skip])
        lines = base_lines[skip:]
        kept = []
        seg_idx = 0
        for line in lines:
            if line.strip():
                if (chunk, seg_idx) in new_lines:
                    kept.append(new_lines[(chunk, seg_idx)])
                else:
                    kept.append(line)
                seg_idx += 1
            else:
                kept.append(line)
        body = '\n'.join(kept)
        io.open(op, 'w', encoding='utf-8').write(head + '\n' + body if head else body)

    print('已標點 %d／%d 段（缺回覆 %d、字詞不符 %d）→ %s'
          % (ok, len(meta), missing, rejected, outdir))


if __name__ == '__main__':
    main()
