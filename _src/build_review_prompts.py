# -*- coding: utf-8 -*-
"""由共用主體＋兩種結尾，產生兩個提示詞版本（共用部分 100% 相同）。

  review_prompt_shared.md          ┐
  review_prompt_ending_jsonl.md    ├─→ review_prompt_universal.md（內部批次／自動發布用）
  review_prompt_ending_plain.md    ┘─→ review_prompt_public.md（公開／人工閱讀用）

用法：python -X utf8 _src/build_review_prompts.py
"""
import io
import os

SRC = os.path.dirname(os.path.abspath(__file__))


def rd(name):
    return io.open(os.path.join(SRC, name), encoding='utf-8').read()


def main():
    shared = rd('review_prompt_shared.md')
    end_jsonl = rd('review_prompt_ending_jsonl.md')
    end_plain = rd('review_prompt_ending_plain.md')
    # 共用主體必須以換行結尾，兩個結尾直接接在其後
    if not shared.endswith('\n'):
        shared += '\n'
    universal = shared + end_jsonl
    public = shared + end_plain
    assert universal.startswith(shared) and public.startswith(shared)
    assert universal[:len(shared)] == public[:len(shared)]
    io.open(os.path.join(SRC, 'review_prompt_universal.md'), 'w',
            encoding='utf-8', newline='\n').write(universal)
    io.open(os.path.join(SRC, 'review_prompt_public.md'), 'w',
            encoding='utf-8', newline='\n').write(public)
    # 只在（三）分岔：共同前綴應到「（三）」之前
    cut = shared.rfind('【輸出格式】')
    assert universal[:cut] == public[:cut]
    print('shared chars:', len(shared))
    print('JSONL version:', len(universal), 'chars')
    print('public version:', len(public), 'chars')
    print('共用前綴檢查:', 'OK（（一）（二）完全一致，只有（三）不同）')


if __name__ == '__main__':
    main()
