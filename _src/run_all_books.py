# -*- coding: utf-8 -*-
"""六部書量產管線：一般段盲翻 → 長段盲翻 → 拼回；可等待既有批次。

用法：
  python -X utf8 _src/run_all_books.py --books 戒疏,尼鈔,行事鈔,資持記 --workers 40
  python -X utf8 _src/run_all_books.py --books 業疏,義鈔 \
      --wait 重譯/業疏/_盲翻,重譯/義鈔/_盲翻 --workers 40
"""
import argparse
import io
import os
import subprocess
import sys
import time

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
T = os.path.join(B, '測試')
PY = sys.executable
STOP = os.path.join(B, 'STOP')


def _stop():
    return os.path.exists(STOP)


def bdir(rel):
    return os.path.join(T, rel.replace('/', os.sep))


def run_agent(batch_rel, workers, raw=True):
    if _stop():
        print('  [STOP] 略過', batch_rel, flush=True)
        return False
    env = dict(os.environ)
    env.update({'QWEN_SHUJI_SRC': batch_rel, 'QWEN_LOCAL': '1', 'QWEN_MAX_FETCH': '1',
                'QWEN_KEEP_THINKING': '1', 'QWEN_400_FALLBACK': '1',
                'QWEN_WORKERS': str(workers),
                'QWEN_RAW_SAVE': '1' if raw else '0',
                'QWEN_NO_CITE': '1' if raw else '0'})
    print('>> 執行', batch_rel, flush=True)
    _r = subprocess.run([PY, '-X', 'utf8', os.path.join(B, '_src', 'qwen_local.py')],
                        cwd=B, env=env)
    if _r.returncode != 0:
        return False
    _d = bdir(batch_rel)
    if os.path.exists(os.path.join(_d, '回覆', '.stage_partial')):
        print('  [部分失敗] 停止：', batch_rel, flush=True)
        return False
    if (os.path.exists(os.path.join(_d, 'STOP'))
            or os.path.exists(os.path.join(_d, '回覆', 'STOPPED.txt'))):
        print('  [已停止] 批次未完成：', batch_rel, flush=True)
        return False
    return True


def call(args, label):
    if _stop():
        print('  [STOP] 略過', label, flush=True)
        return False
    print('>> ', label, flush=True)
    r = subprocess.run([PY, '-X', 'utf8'] + args, cwd=B)
    return r.returncode == 0


def count_replies(rel):
    d = os.path.join(bdir(rel), '回覆')
    if not os.path.isdir(d):
        return 0
    return len([f for f in os.listdir(d) if f.endswith('_回.txt')])


def count_materials(rel):
    d = bdir(rel)
    if not os.path.isdir(d):
        return 0
    return len([f for f in os.listdir(d) if f.endswith('.md')])


def wait_batch(rel, timeout_h=30):
    total = count_materials(rel)
    t0 = time.time()
    while time.time() - t0 < timeout_h * 3600:
        if _stop():
            return False
        _bd = bdir(rel)
        if os.path.exists(os.path.join(_bd, '回覆', '.stage_partial')):
            print('  [部分失敗] 停止等待：', rel, flush=True)
            return False
        done = count_replies(rel)
        if total and done >= total:
            print('  已等完', rel, '（%d 份）' % done, flush=True)
            return True
        time.sleep(60)
    print('  等待逾時：', rel, flush=True)
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--books', required=True)
    ap.add_argument('--workers', type=int, default=40)
    ap.add_argument('--wait', default='')
    ap.add_argument('--skip-blind', action='store_true')
    args = ap.parse_args()

    for rel in [x.strip() for x in args.wait.split(',') if x.strip()]:
        print('等待既有批次：', rel, flush=True)
        if not wait_batch(rel):
            return

    for bk in [x.strip() for x in args.books.split(',') if x.strip()]:
        _hy = '重譯/' + bk + '/_hy_盲翻'
        if _stop():
            print('收到 STOP，結束', flush=True)
            return
        root = '重譯/' + bk
        print('===== %s =====' % bk, flush=True)
        if not args.skip_blind:
            _bdir = root + '/_hy_盲翻' if os.path.isdir(bdir(root + '/_hy_盲翻')) else root + '/_盲翻'
            if not run_agent(_bdir, args.workers, raw=True):
                return
        if os.path.isdir(bdir(root + '/_長段/_盲翻')) and count_materials(root + '/_長段/_盲翻'):
            if not run_agent(root + '/_長段/_盲翻', args.workers, raw=True):
                return
            call(['_src/merge_long.py', '--book', bk], '拼回長段：' + bk)
            call(['_src/run_long_audit.py', '--book', bk, '--audit-run'], '長段終審：' + bk)
            call(['_src/build_a2.py', '--blind', '測試/' + root + '/_長段/_盲翻',
                  '--base', '測試/' + root + '/_長段/_終審材料',
                  '--audit', '測試/' + root + '/_長段/_終審',
                  '--revise', '測試/' + root + '/_長段/_終修',
                  '--out', '測試/' + root + '/_長段/_定稿'], '長段定稿：' + bk)
        print('===== %s 完成 =====' % bk, flush=True)
    print('全部書目完成', flush=True)


if __name__ == '__main__':
    main()
