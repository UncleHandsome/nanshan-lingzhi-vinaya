# 對話材料 #0742

- event: assistant/message
- seq: 102121
- time: 1794952506508

---

{"command": "$ROOT='C:\\Users\\lionc\\OneDrive\\桌面\\XW\\三大部'\n$env:PYTHONIOENCODING='utf-8'\n$py='C:\\Users\\lionc\\.dsh\\dsh-runtimes\\dsh-primary-runtime\\dependencies\\python\\python.exe'\n& $py -X utf8 -c @\"\nimport io,os\nkeys=['00_卷首_L0005','01a_卷上之一_L0008','01a_卷上之一_L0014','01a_卷上之一_L0015','01b_卷上之一_L0001','01b_卷上之一_L0004']\nd=r'$ROOT\\測試\\重譯\\義鈔\\_長段\\_終審材料'\nfor k in keys:\n    p=os.path.join(d,k+'.md')\n    if os.path.exists(p):\n        t=io.open(p,encoding='utf-8').read(); print(k,'blocks',t.count('【鈔文】'),'len',len(t))\n    else: print(k,'missing')\np=r'$ROOT\\測試\\重譯\\_長段修訂材料_20261118\\前六個_譯文.md'\nt=io.open(p,encoding='utf-8').read(); print('output blocks',t.count('【鈔文】'),'len',len(t))\n\"@", "description": "Count 鈔文 blocks per first-six material", "timeoutMs": 120000}