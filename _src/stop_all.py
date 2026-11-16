# -*- coding: utf-8 -*-
"""一鍵優雅停止：在專案根目錄與所有批次目錄放 STOP 檔。

用法：
  python -X utf8 _src/stop_all.py           # 停止全部
  python -X utf8 _src/stop_all.py --clear   # 清除所有 STOP（恢復）
"""
import argparse
import io
import os
import time

B = r'C:\Users\lionc\OneDrive\桌面\XW\三大部'
T = os.path.join(B, '測試')


def batch_dirs():
    """找出所有含『回覆』子目錄的批次目錄。"""
    out = []
    for root, dirs, _files in os.walk(T):
        if '回覆' in dirs:
            out.append(root)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--clear', action='store_true')
    args = ap.parse_args()

    targets = [B] + batch_dirs()
    n = 0
    for d in targets:
        p = os.path.join(d, 'STOP')
        if args.clear:
            if os.path.exists(p):
                os.remove(p)
                n += 1
                print('  清除', p)
        else:
            io.open(p, 'w', encoding='utf-8').write('stop %s\n' % time.strftime('%Y-%m-%d %H:%M:%S'))
            n += 1
            print('  標記', p)
    print(('已清除 %d 處 STOP' if args.clear else '已標記 %d 處 STOP') % n)


if __name__ == '__main__':
    main()
