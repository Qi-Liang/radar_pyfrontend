# 作者     ：gw
# 创建日期 ：2019-10-08  下午 16:10
# 文件名   ：data_process.py


import json
import numpy as np

res = []
test_data = {"1": [{"x": 2, "y": 4, "z": 5}, {"x": 3, "y": 4, "z": 2}, {"x": 1, "y": 7, "z": 4}],
             "2": [{"x": 2, "y": 2, "z": 6}, {"x": 3, "y": 4, "z": 8}, {"x": 5, "y": 7, "z": 6}],
             "3": [{"x": 5, "y": 7, "z": 2}, {"x": 1, "y": 5, "z": 6}, {"x": 7, "y": 2, "z": 1}],
             }
for i in test_data:
    t = []
    for j in test_data[i]:
        tt = [j['x'], j['y'], j['z']]
        t.append(tt)
    res.append(t)

print(res)

res2 = np.array(res)
print(res2)
print(res2.shape)