import sys
sys.path.insert(0,r"C:\Users\lionc\OneDrive\桌面\XW\三大部\AI語譯\_work\review")
import _rv_dig2 as D
print(D.header_segs("## 【895-0001】"))
print(D.LEAD.pattern)
import re
print(repr(D.LEAD.sub("", "## 【895-0001】")))
