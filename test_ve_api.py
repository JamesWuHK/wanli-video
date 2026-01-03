import requests
import json

api_key = "sk-hSsIao5zgH3uctxxJqWZOezaSW2HZWFTf8HHJQgL6mav6cpJ"

# 测试简单的文本请求
url = "https://api.vectorengine.ai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 简单的文本测试
payload = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {"role": "user", "content": "Hello, can you respond?"}
    ]
}

print("测试1: 简单文本请求")
response = requests.post(url, headers=headers, json=payload)
print(f"状态码: {response.status_code}")
print(f"响应: {response.text[:200]}")
print()

# 测试 sora-2 模型
print("测试2: sora-2 模型文本请求")
payload2 = {
    "model": "sora-2",
    "messages": [
        {"role": "user", "content": "一段壮丽的山河视频"}
    ]
}

response2 = requests.post(url, headers=headers, json=payload2)
print(f"状态码: {response2.status_code}")
print(f"响应: {response2.text[:500]}")
