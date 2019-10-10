# 作者     ：gw
# 创建日期 ：2019-10-08  下午 16:10
# 文件名   ：data_process.py


import json

res = []
with open(r'hi.json', 'r', encoding='utf-8') as f:
    txt = json.load(f)
    for i in txt:
        t = []
        for j in txt[i]:
            tt = [j['x'], j['y'], j['z']]
            t.append(tt)
        res.append(t)

print(res)