import json, os, collections
rows = json.load(open(os.path.join(os.path.dirname(__file__), "m2_rows.json"), encoding="utf-8"))
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
files = {}
for r in rows:
    files.setdefault(r["file"], []).append(r["seg"])
for f, segs in sorted(files.items()):
    b = open(f, "rb").read()
    bom = b.startswith(b"\xef\xbb\xbf")
    crlf = b.count(b"\r\n"); lf = b.count(b"\n") - crlf; cr = b.count(b"\r") - crlf
    txt = b.decode("utf-8-sig")
    lines = txt.split("\n")
    ne = [l for l in lines if l.strip()]
    print("%-58s BOM=%s crlf=%d lf=%d cr=%d paras=%d segs=%s" % (
        os.path.relpath(f, ROOT), bom, crlf, lf, cr, len(ne), ",".join(map(str, sorted(segs)))))
