# -*- coding: utf-8 -*-
"""吸收校閱結果：把已跑過的檔案移到 new/已完成/<批次>/，並重建 index。

判定「已跑過」的依據（兩種都支援）：
  1. 報告中出現過的編號（NN-NNNN）→ 該檔已跑。
  2. 報告中的「檔案編號：NN-xxxx ～ NN-yyyy」→ 即使零問題也算已跑。

用法：
    python _src/absorb_review.py 校閱批次/new/re6.txt re6
"""
import os, io, re, sys, glob, shutil

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
D = os.path.join(B, '校閱批次')


def covered_nums(text):
    nums = set()
    for m in re.finditer(r'(?m)^(?:###\s*)?(?:【)?([0-9]{2,3})-[0-9]{4}', text):
        nums.add(int(m.group(1)))
    # 檔案編號行：抓兩端
    for m in re.finditer(r'檔案編號[：:]\s*([0-9]{2,3})-[0-9]{4}\s*[～~\-–]\s*([0-9]{2,3})-[0-9]{4}', text):
        a, b = int(m.group(1)), int(m.group(2))
        nums.update(range(min(a, b), max(a, b) + 1))
    return sorted(nums)


def rebuild_index():
    rows = []
    for f in sorted(glob.glob(os.path.join(D, '校閱_*.txt'))):
        t = io.open(f, encoding='utf-8').read()
        body = t.split('# 材料開始', 1)[1] if '# 材料開始' in t else t
        segs = len(re.findall(r'【[0-9]{2,3}-[0-9]{4}】', body))
        m = re.search(r'】([^/\n]+)/', body)
        book = m.group(1) if m else '?'
        grp = {'資持記': '鈔記', '01_行事鈔': '鈔記', '02_戒疏': '戒疏',
               '03_業疏': '業疏', '04_比丘尼鈔': '尼鈔', '05_拾毗尼義鈔': '義鈔'}.get(book, book)
        rows.append((os.path.basename(f), grp, segs, os.path.getsize(f)))
    with io.open(os.path.join(D, 'index.tsv'), 'w', encoding='utf-8') as fh:
        fh.write('file\tgroup\tsegs\tbytes\n')
        for r in rows:
            fh.write('%s\t%s\t%d\t%d\n' % r)
    return len(rows), sum(r[2] for r in rows)


def main():
    if len(sys.argv) < 3:
        print('用法：python _src/absorb_review.py <報告檔> <批次名>')
        return 1
    report, tag = sys.argv[1], sys.argv[2]
    text = io.open(report, encoding='utf-8').read()
    nums = covered_nums(text)
    dst = os.path.join(D, 'new', '已完成', tag)
    os.makedirs(dst, exist_ok=True)
    moved, missing = [], []
    for n in nums:
        p = os.path.join(D, '校閱_%02d.txt' % n)
        if os.path.exists(p):
            shutil.move(p, os.path.join(dst, os.path.basename(p)))
            moved.append(n)
        else:
            missing.append(n)
    total, segs = rebuild_index()
    print('報告涵蓋 %d 檔；已移出 %d 檔；找不到 %d 檔（可能已移過）' % (len(nums), len(moved), len(missing)))
    print('剩餘 %d 檔、%d 段' % (total, segs))
    return 0


if __name__ == '__main__':
    sys.exit(main())
