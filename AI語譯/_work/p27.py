import sys
sys.stdout.reconfigure(encoding="utf-8")
for p in [r"存疑材料\complex_存疑\round2.md", r"AI語譯\_work\review\說明_存疑1.md", r"AI語譯\_work\review\說明_存疑套用.md"]:
    b=open(p,"rb").read()
    print(p, "CRLF", b.count(b"\r\n"), "LF", b.count(b"\n"), "BOM", b[:3]==b"\xef\xbb\xbf")
