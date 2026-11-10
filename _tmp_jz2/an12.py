# -*- coding: utf-8 -*-
import importlib.util
spec = importlib.util.spec_from_file_location("fx", r"C:\Users\lionc\OneDrive\桌面\XW\三大部\_src\fix_hebian_jz2.py")
fx = importlib.util.module_from_spec(spec); spec.loader.exec_module(fx)
yp = fx.yuan_pairs()
ji = [r['num'] for r in yp if r['kind']=='記']
ch = [r['num'] for r in yp if r['kind']=='鈔']
print('鈔', min(ch), max(ch), len(ch))
print('記', min(ji), max(ji), len(ji), 'unique', len(set(ji)))
dups = sorted(n for n in set(ji) if ji.count(n)>1)
print('重號', dups)
