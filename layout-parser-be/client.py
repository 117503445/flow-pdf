# pip install requests

import requests

# 定义上传文件接口地址
url = "http://localhost:8000/api/parse_pdf"

# 发送 POST 请求并上传图片
response = requests.post(url, files={"file": open("./example/hotstuff.pdf", "rb")})

# 输出结果
print(response.json())