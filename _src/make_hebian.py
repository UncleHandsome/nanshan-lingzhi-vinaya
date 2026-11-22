# -*- coding: utf-8 -*-
"""重建合編本：定稿 JSONL → docs/hebian（不再經 docx）。"""
import os
import subprocess
import sys

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
PY = sys.executable
SRC = os.path.join(B, '_src')


def run(script, args):
    p = subprocess.run([PY, '-X', 'utf8', os.path.join(SRC, script)] + args, cwd=B,
                       capture_output=True, text=True, encoding='utf-8')
    print(script, p.returncode, (p.stdout or '').strip().split('\n')[-2:], flush=True)
    if p.returncode != 0:
        print((p.stderr or '')[-800:], flush=True)
    return p.returncode == 0


def main():
    if not run('site_hebian.py', []):
        print('site_hebian 失敗，停止')
        return 1
    if not run('validate_site.py', ['--book', 'hebian']):
        print('validate_site 失敗')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
