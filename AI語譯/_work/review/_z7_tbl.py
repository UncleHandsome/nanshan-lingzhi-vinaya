import io,json
rows=[json.loads(l) for l in io.open("_z7_log.jsonl",encoding="utf-8") if l.strip()]
for r in rows:
    print("| %d | %d | %d | %d | %d | %d |"%(r["n"],r["segs"],r["yi"],r["run"],r["veto"],r["doubt"]))
