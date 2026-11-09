# -*- coding: utf-8 -*-
import json, re, io
rows = json.load(open(r"AI語譯\_work\review\_re4g1\rows.json", encoding="utf-8"))
def occ(s, sub):
    return s.count(sub)
for i in (59,72,139,96,67):
    r = rows[i-1]; print("R%d" % i)
# check duplicates of old for R139 etc
checks = {139:"應當制立", 59:"因為主持其事的人喜好詳盡廣博", 72:"感念佛恩：", 96:"若論宣說雖然有一處與多處的微細差異", 67:"依據其聚眾和合之相來翻譯", 33:"這是列舉譬喻來說明戒的功用，是依據能說之喻來立論", 32:"如果依照法義來判斷經文"}
for k,v in checks.items():
    r = rows[k-1]
    print("R%d count=%d len=%d seg=%s" % (k, r["current"].count(v), len(r["current"]), r["seg"]))
# print seg 100 and 109 context
for k in (59,139):
    r = rows[k-1]; cur = r["current"]
    print("---- R%d FULL: %s" % (k, cur[:700]))
