# pip install requests

import time
import requests

# 定义上传文件接口地址
url = "http://localhost:8000/api/task"

# 发送 POST 请求并上传图片
response = requests.post(url, files={"file": open("./example/hotstuff.pdf", "rb")})

# 输出结果
print(response.json())

task_id = response.json()['data']['taskID']

while True:
    resp = requests.get(url+f'/{task_id}').json()
    print(resp['code'], resp['msg'])
    if resp['code'] == 0:
        break
    time.sleep(5)

print(resp['data'])