# -*- coding: utf-8 -*-
"""依序跑一個書的多個階段（盲翻→裁決→審核→修訂→定稿），支援 STOP 與失敗即停。

用法：
  python -X utf8 _src/run_pipeline.py --book 業疏 --stages judge,audit,revise,final
  python -X utf8 _src/run_pipeline.py --book 業疏 --stages packjudge,audit,revise,final
  python -X utf8 _src/run_pipeline.py --book 業疏 --stages long
"""
import argparse
import os
import shutil
import subprocess
import sys
import time

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
T = os.path.join(B, '測試')
PY = sys.executable
STOP = os.path.join(B, 'STOP')


def _stop():
    return os.path.exists(STOP)


def batch_dir(p):
    return os.path.join(T, p.replace('/', os.sep))


def run_agent(batch, extra_env=None, workers=20):
    if _stop():
        print('  [停止] 略過', batch, flush=True)
        return False
    env = dict(os.environ)
    env.update({'QWEN_SHUJI_SRC': batch, 'QWEN_LOCAL': '1',
                'QWEN_KEEP_THINKING': '1', 'QWEN_400_FALLBACK': '1',
                'QWEN_WORKERS': str(workers)})
    if extra_env:
        env.update(extra_env)
    print('>> 執行', batch, flush=True)
    r = subprocess.run([PY, '-X', 'utf8', os.path.join(B, '_src', 'qwen_local.py')],
                       cwd=B, env=env)
    if r.returncode != 0:
        print('  [失敗] 執行器回傳', r.returncode, flush=True)
        return False
    d = batch_dir(batch) if not os.path.isabs(batch) else batch
    if os.path.exists(os.path.join(d, '回覆', '.stage_partial')):
        print('  [部分失敗] 有缺檔或截斷，停止往下推：', batch, flush=True)
        return False
    if (os.path.exists(os.path.join(d, 'STOP'))
            or os.path.exists(os.path.join(d, '回覆', 'STOPPED.txt'))):
        print('  [已停止] 批次未完成：', batch, flush=True)
        return False
    return True


def call(args, label):
    if _stop():
        print('  [停止] 略過', label, flush=True)
        return False
    print('>> 產生', label, flush=True)
    r = subprocess.run([PY, '-X', 'utf8'] + args, cwd=B)
    if r.returncode != 0:
        print('!! 失敗', label, flush=True)
    return r.returncode == 0


def wait_done(batch, timeout_h=24):
    base = batch_dir(batch)
    d = os.path.join(base, '回覆')
    total = len([f for f in os.listdir(base) if f.endswith('.md')]) if os.path.isdir(base) else 0
    end = time.time() + timeout_h * 3600
    while time.time() < end:
        if _stop():
            return False
        if os.path.exists(os.path.join(d, '.stage_partial')):
            return False
        n = len([f for f in os.listdir(d) if f.endswith('_回.txt')]) if os.path.isdir(d) else 0
        if total and n >= total:
            return True
        time.sleep(60)
    return False


def _mat(root):
    hy = root + '/_材料_hy'
    base = root + '/_材料'
    if os.path.isdir(batch_dir(hy)):
        _mh = os.path.getmtime(batch_dir(hy))
        _mb = os.path.getmtime(batch_dir(base)) if os.path.isdir(batch_dir(base)) else 0
        return hy if _mh >= _mb else base
    return base


def _blind(root):
    hy = root + '/_hy_盲翻'
    base = root + '/_盲翻'
    if os.path.isdir(batch_dir(hy + '/回覆')):
        _mh = os.path.getmtime(batch_dir(hy))
        _mb = os.path.getmtime(batch_dir(base)) if os.path.isdir(batch_dir(base)) else 0
        return hy if _mh >= _mb else base
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--book', required=True)
    ap.add_argument('--wait', default='')
    ap.add_argument('--stages', default='judge,audit,revise,final')
    ap.add_argument('--workers', type=int, default=20)
    args = ap.parse_args()

    bk = args.book
    root = '重譯/' + bk
    if args.wait:
        print('等待批次完成：', args.wait, flush=True)
        if not wait_done(args.wait):
            print('等待中止（超時或收到 STOP）', flush=True)
            return

    stages = [s.strip() for s in args.stages.split(',') if s.strip()]
    for st in stages:
        if _stop():
            print('收到 STOP，結束', flush=True)
            return

        if st == 'review':
            if not run_agent(_mat(root), {'QWEN_RAW_SAVE': '0', 'QWEN_NO_CITE': '0',
                                          'QWEN_KEEP_THINKING': '1'}, args.workers):
                return

        elif st in ('judge', 'packjudge'):
            out_mat = '測試/' + root + ('/_裁決_材料' if st == 'packjudge' else '/_裁決')
            if not call(['_src/mk_judge_materials.py', '--src', '測試/' + _mat(root),
                         '--a', '測試/' + _blind(root) + '/回覆', '--b', 'out',
                         '--out', out_mat], '裁決材料'):
                return
            if st == 'judge':
                if not run_agent(root + '/_裁決', {'QWEN_RAW_SAVE': '0', 'QWEN_NO_CITE': '0',
                                                   'QWEN_KEEP_THINKING': '1'}, args.workers):
                    return
            else:
                if not call(['_src/pack_judge.py', '--materials', '測試/' + root + '/_裁決_材料',
                             '--out', '測試/' + root + '/_裁決_pack', '--mode', 'pack'], '裁前打包'):
                    return
                if not run_agent(root + '/_裁決_pack', {'QWEN_RAW_SAVE': '0', 'QWEN_NO_CITE': '0',
                                                        'QWEN_KEEP_THINKING': '1'}, args.workers):
                    return
                if not call(['_src/pack_judge.py', '--out', '測試/' + root + '/_裁決_pack',
                             '--mode', 'split', '--replies', '回覆',
                             '--mat', '測試/' + root + '/_裁決_材料'], '拆回裁決'):
                    return
                src = batch_dir(root + '/_裁決_pack/_拆回')
                dst = batch_dir(root + '/_裁決')
                if os.path.isdir(src):
                    if os.path.isdir(dst):
                        shutil.rmtree(dst, ignore_errors=True)
                    os.makedirs(dst, exist_ok=True)
                    for f in os.listdir(src):
                        if f.endswith(('.md', '.json')):
                            shutil.copy2(os.path.join(src, f), os.path.join(dst, f))
                    os.makedirs(os.path.join(dst, '回覆'), exist_ok=True)
                    for f in os.listdir(os.path.join(src, '回覆')):
                        if f.endswith('_回.txt'):
                            shutil.copy2(os.path.join(src, '回覆', f),
                                         os.path.join(dst, '回覆', f))

        elif st == 'long':
            if not call(['_src/mk_split_blind.py', '--book', bk], '長段切分'):
                return
            if not run_agent('重譯/' + bk + '/_長段/_盲翻',
                             {'QWEN_RAW_SAVE': '1', 'QWEN_NO_CITE': '1'}, args.workers):
                return
            if not call(['_src/merge_long.py', '--book', bk], '長段拼回'):
                return
            if not call(['_src/run_long_audit.py', '--book', bk], '長段終審材料'):
                return
            if not run_agent('重譯/' + bk + '/_長段/_終審',
                             {'QWEN_RAW_SAVE': '1', 'QWEN_NO_CITE': '0'}, args.workers):
                return
            if not call(['_src/mk_revise_materials.py',
                         '--r1', '測試/' + root + '/_長段/_終審材料',
                         '--audit', '測試/' + root + '/_長段/_終審',
                         '--out', '測試/' + root + '/_長段/_終修'], '長段修訂材料'):
                return
            if not run_agent('重譯/' + bk + '/_長段/_終修',
                             {'QWEN_RAW_SAVE': '1', 'QWEN_NO_CITE': '1', 'QWEN_NO_TOOLS': '1',
                              'QWEN_LOCAL': '0', 'QWEN_EFFORT': 'xhigh'}, args.workers):
                return
            if not call(['_src/build_a2.py', '--blind', '測試/' + root + '/_長段/_盲翻',
                         '--base', '測試/' + root + '/_長段/_終審材料',
                         '--audit', '測試/' + root + '/_長段/_終審',
                         '--revise', '測試/' + root + '/_長段/_終修',
                         '--out', '測試/' + root + '/_長段/_定稿'], '長段定稿'):
                return

        elif st == 'audit':
            if not call(['_src/mk_audit_materials.py', '--src', '測試/' + root + '/_裁決',
                         '--out', '測試/' + root + '/_終審'], '終審材料'):
                return
            if not run_agent(root + '/_終審', {'QWEN_RAW_SAVE': '1', 'QWEN_NO_CITE': '0',
                                               'QWEN_KEEP_THINKING': '1'}, args.workers):
                return

        elif st == 'revise':
            if not call(['_src/mk_revise_materials.py', '--r1', '測試/' + root + '/_裁決',
                         '--audit', '測試/' + root + '/_終審',
                         '--out', '測試/' + root + '/_終修'], '修訂材料'):
                return
            if not run_agent(root + '/_終修', {'QWEN_RAW_SAVE': '1', 'QWEN_NO_CITE': '1',
                                               'QWEN_NO_TOOLS': '1', 'QWEN_LOCAL': '0',
                                               'QWEN_EFFORT': 'xhigh',
                                               'QWEN_KEEP_THINKING': '1'}, args.workers):
                return

        elif st == 'final':
            if not call(['_src/build_a2.py', '--blind', '測試/' + _blind(root),
                         '--base', '測試/' + root + '/_裁決',
                         '--audit', '測試/' + root + '/_終審',
                         '--revise', '測試/' + root + '/_終修',
                         '--out', '測試/' + root + '/_定稿'], '定稿'):
                return
        else:
            print('未知階段：', st, flush=True)
            return

    print('流程結束：', bk, flush=True)


if __name__ == '__main__':
    main()
