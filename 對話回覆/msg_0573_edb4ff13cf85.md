# 對話材料 #0573

- event: assistant/message
- seq: 83901
- time: 1794807433936

---

{"command": "$env:PYTHONIOENCODING='utf-8'\n$py='C:\\Users\\lionc\\.dsh\\dsh-runtimes\\dsh-primary-runtime\\dependencies\\python\\python.exe'\n$ROOT='C:\\Users\\lionc\\OneDrive\\桌面\\XW\\三大部'\n& $py -X utf8 -c @\"\nimport io,os\nbody='''【疏文】有人說：「這是由於造作超過規定尺寸而犯戒，並不是說在符合規定尺寸下仍有貯存積畜之罪。正如《善見》所說：『如果沙彌與大僧多人共同建造，不犯戒。若逐段計算分出單間房舍，因超過規定尺寸，也同樣犯戒。』」\n【記文】他家解釋一段中。意思是說，造房與畜長不能比照等同：畜長若是共同貯畜就會犯戒，造房若是共同建造則沒有過失。「如」字以下，是引據證明不犯戒。必須就逐段計算超過規定尺寸來說，才有犯戒的道理。'''\ndd=os.path.join(r'$ROOT','測試','blocked待處理','已翻譯','戒疏'); os.makedirs(dd,exist_ok=True)\nio.open(os.path.join(dd,'766.txt'),'w',encoding='utf-8').write(body+'\\n')\nflat=os.path.join(r'$ROOT','測試','blocked待處理','重翻','全部待翻')\nfor f in list(os.listdir(flat)):\n    if f.startswith('戒疏_766'): os.remove(os.path.join(flat,f))\nprint('flat 剩:',os.listdir(flat))\nfor bk in ('尼鈔','戒疏','行事鈔','業疏','義鈔','資持記'):\n    d=os.path.join(r'$ROOT','測試','blocked待處理','已翻譯',bk)\n    if os.path.isdir(d):\n        print(bk,len([f for f in os.listdir(d) if f.endswith('.txt') and not f.startswith('_')]))\n\"@", "description": "Save final 766 translation and confirm pending empty", "timeoutMs": 120000}