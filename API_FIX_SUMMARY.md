# VectorEngine API 调用修复总结

## ✅ 问题已解决

### 之前的问题
- ❌ 使用了错误的 API 端点：`/v1/chat/completions`
- ❌ 使用了错误的请求格式（OpenAI chat格式）
- ❌ 导致 429/400 错误

### 正确的调用方式

**端点**: `/v1/video/create` （VectorEngine 统一视频格式）

**请求格式**: JSON

**请求体**:
```json
{
  "model": "sora-2",
  "prompt": "视频描述文字",
  "image": "data:image/png;base64,<base64编码的图片>",
  "size": "1280x720",
  "duration": 10
}
```

**支持的参数**:
- `model`: sora-2, sora-2-all 等
- `size`: 1280x720 (16:9) 或 720x1280 (9:16)
- `duration`: 10秒 或 15秒

**定价**（sora-2模型）:
- 1280x720, 10秒: ¥0.30
- 1280x720, 15秒: ¥0.45

## 🎯 当前状态

✅ **API 客户端已修复** - [vectorengine_client.py](scripts/vectorengine_client.py)

⏸️ **服务器仍在高峰期** - 返回错误："当前分组上游负载已饱和，请稍后再试"

## 📝 下一步

### 等服务器可用后运行

```bash
# 测试单个视频
export VECTORENGINE_API_KEY="sk-hSsIao5zgH3uctxxJqWZOezaSW2HZWFTf8HHJQgL6mav6cpJ"
python3 scripts/vectorengine_client.py \
  --api-key "$VECTORENGINE_API_KEY" \
  --image "storyboards/文脉薪传/keyframes/scene_01_opening_keyframe.png" \
  --prompt "壮丽的中国山河全景" \
  --model "sora-2" \
  --output "test.mp4"
```

### 批量生成所有视频

```bash
export VECTORENGINE_API_KEY="sk-hSsIao5zgH3uctxxJqWZOezaSW2HZWFTf8HHJQgL6mav6cpJ"
export USE_AI=true
export AI_MODEL=sora-2
python3 scripts/generate_dynamic_videos_vectorengine.py
```

### 使用 Docker

```bash
docker run --rm \
  -v /Users/wujames/cursor_prj/wanli-qingyun-project/storyboards:/app/storyboards \
  -e VECTORENGINE_API_KEY="sk-hSsIao5zgH3uctxxJqWZOezaSW2HZWFTf8HHJQgL6mav6cpJ" \
  -e USE_AI=true \
  -e AI_MODEL=sora-2 \
  video-generator:latest
```

## 🔍 验证 API 可用性

在运行前，先测试服务器状态：

```bash
python3 << 'EOF'
import requests
import base64
from pathlib import Path

api_key = "sk-hSsIao5zgH3uctxxJqWZOezaSW2HZWFTf8HHJQgL6mav6cpJ"
image_path = Path("storyboards/文脉薪传/keyframes/scene_01_opening_keyframe.png")

with open(image_path, 'rb') as f:
    image_base64 = base64.b64encode(f.read()).decode('utf-8')

response = requests.post(
    "https://api.vectorengine.ai/v1/video/create",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json={
        "model": "sora-2",
        "prompt": "测试",
        "image": f"data:image/png;base64,{image_base64}",
        "size": "1280x720",
        "duration": 10
    },
    timeout=60
)

print(f"状态码: {response.status_code}")
print(f"响应: {response.json()}")
EOF
```

**成功标志**:
- 状态码 200
- 响应包含 `id` 和 `status`
- `status` 为 `pending` 或 `processing`（不是 `error`）

**失败标志**:
- 状态码 500
- 响应包含 "当前分组上游负载已饱和"

## 📊 成本预估（修复后）

### sora-2 模型（推荐）

**混合方案**（13个场景，10秒）:
```
13 × ¥0.30 = ¥3.90
```

**混合方案**（13个场景，15秒）:
```
13 × ¥0.45 = ¥5.85
```

**仅开场+结局**（2个场景，10秒）:
```
2 × ¥0.30 = ¥0.60
```

## 🎬 API 文档参考

- **VectorEngine API 端点**: https://api.vectorengine.ai/v1
- **支持的端点**:
  - `/v1/chat/completions` - OpenAI chat格式
  - `/v1/video/create` - 统一视频格式（**推荐用于图生视频**）
  - `/v1/videos` - OpenAI官方视频格式

## 📝 技术细节

### API 响应格式

**成功响应**:
```json
{
  "id": "video_xxxxx",
  "status": "pending",  // 或 "processing", "completed"
  "url": "https://..."   // 视频URL（完成后）
}
```

**错误响应**:
```json
{
  "id": "",
  "status": "error",
  "error": "当前分组上游负载已饱和，请稍后再试"
}
```

### 异步处理

视频生成是异步的：
1. 提交请求 → 返回 `id` 和 `status: pending`
2. 轮询状态 → `GET /v1/video/query/{id}`
3. 等待完成 → `status: completed`
4. 下载视频 → 从响应中的 `url` 字段

---

**最后更新**: 2026-01-03

**状态**: ✅ API修复完成，⏸️ 等待服务器可用
