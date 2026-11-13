# -*- coding: utf-8 -*-
"""檢查／套用 _7kv2_edits.py 的修訂。預設只檢查，--apply 才寫檔（先備份 v2）。"""
import io, os, shutil, sys, difflib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _7kv2_edits import EDITS

ROOT = r"C:\Users\lionc\OneDrive\桌面\XW\三大部"
CHUNK = "06c_卷中之二"
OUT = os.path.join(ROOT, "AI語譯", "out", "01_行事鈔", CHUNK + ".txt")
BAK = os.path.join(ROOT, "歸檔", "7K卷修正前", "01_行事鈔", CHUNK + "_v2.txt")


def main():
    apply = "--apply" in sys.argv
    raw = io.open(OUT, encoding="utf-8", newline="").read()
    assert "\r" not in raw, "unexpected CR"
    lines = raw.split("\n")

    # segment no -> line index (non-empty paragraphs)
    seg_lines = {}
    n = 0
    for i, ln in enumerate(lines):
        if ln.strip():
            n += 1
            seg_lines[n] = i
    print("paragraphs:", n)

    ok = True
    for seg, old, new, note in EDITS:
        li = seg_lines.get(seg)
        if li is None:
            print("!! seg not found", seg)
            ok = False
            continue
        cnt = lines[li].count(old)
        if cnt != 1:
            print("!! count=%d seg=%d %s :: %r" % (cnt, seg, note, old[:80]))
            ok = False
    if not ok:
        print("HAS FAILURES — not writing")
        return 1

    print("all %d edits match exactly once" % len(EDITS))
    if not apply:
        print("dry-run OK; use --apply to write")
        return 0

    if not os.path.exists(BAK):
        os.makedirs(os.path.dirname(BAK), exist_ok=True)
        shutil.copy2(OUT, BAK)
        print("backup ->", BAK)
    else:
        print("backup exists:", BAK)

    before = {}
    for seg, old, new, note in EDITS:
        before.setdefault(seg, lines[seg_lines[seg]])
        lines[seg_lines[seg]] = lines[seg_lines[seg]].replace(old, new, 1)

    out_text = "\n".join(lines)
    io.open(OUT, "w", encoding="utf-8", newline="").write(out_text)
    print("written", OUT, len(out_text), "chars")

    # show changed paragraphs count
    changed = sorted(before)
    print("changed segments:", changed, "count", len(changed))
    for seg in changed:
        a, b = before[seg], lines[seg_lines[seg]]
        sm = difflib.SequenceMatcher(None, a, b)
        print("seg %d similarity %.4f" % (seg, sm.ratio()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
