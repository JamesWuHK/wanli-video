# 启用 VectorEngine AI 视频生成指南

## 🎯 当前状态

- ✅ **本地 Ken Burns 效果视频**已生成（13个场景）
- ✅ **完整版视频**已合成（90.7秒，16MB）
- ⏸️ **VectorEngine sora-2 AI 生成**：服务器当前负载高峰，返回 429 错误

## 🚀 等服务器可用后，如何启用 AI 生成

### 方法 1: 使用 Docker（推荐）

```bash
# 1. 设置 API Key 环境变量
export VECTORENGINE_API_KEY="sk-hSsIao5zgH3uctxxJqWZOezaSW2HZWFTf8HHJQgL6mav6cpJ"

# 2. 重新构建 Docker 镜像（启用 AI）
docker build -t video-generator:ai --build-arg USE_AI=true .

# 3. 运行 AI 视频生成
docker run --rm \
  -v /Users/wujames/cursor_prj/wanli-qingyun-project/storyboards:/app/storyboards \
  -e VECTORENGINE_API_KEY="$VECTORENGINE_API_KEY" \
  -e USE_AI=true \
  -e AI_MODEL=sora-2 \
  video-generator:ai
```

### 方法 2: 直接运行（需要安装依赖）

```bash
# 1. 安装 Python 依赖
pip3 install pyyaml edge-tts requests

# 2. 设置环境变量
export VECTORENGINE_API_KEY="sk-hSsIao5zgH3uctxxJqWZOezaSW2HZWFTf8HHJQgL6mav6cpJ"
export USE_AI=true
export AI_MODEL=sora-2

# 3. 运行生成
python3 scripts/generate_dynamic_videos_vectorengine.py
```

### 方法 3: 只对特定场景使用 AI

编辑 `scripts/generate_dynamic_videos_vectorengine.py`：

```python
def is_key_scene(self, scene: Dict) -> bool:
    """自定义哪些场景使用 AI"""
    # 只对这些场景使用 AI
    ai_scenes = [
        'scene_01_opening',      # 开场
        'scene_07_grand_finale'  # 结局
    ]
    return scene['id'] in ai_scenes
```

然后运行：
```bash
export VECTORENGINE_API_KEY="sk-hSsIao5zgH3uctxxJqWZOezaSW2HZWFTf8HHJQgL6mav6cpJ"
export USE_AI=true
python3 scripts/generate_dynamic_videos_vectorengine.py
```

---

## 💰 成本估算

### 默认混合方案（关键分镜用 AI）

当前脚本会自动识别 **13 个关键分镜**（所有场景时长都 ≥ 10秒）：

```
关键分镜：13 个 × ¥0.030 = ¥0.39
普通分镜：0 个 × ¥0 (Ken Burns) = ¥0
---------------------------------------
总成本：¥0.39
```

### 仅开场和结局用 AI（推荐测试）

```
关键分镜：2 个 × ¥0.030 = ¥0.06
普通分镜：11 个 × ¥0 (Ken Burns) = ¥0
---------------------------------------
总成本：¥0.06
```

### 所有场景都用 AI

```
全部场景：13 个 × ¥0.030 = ¥0.39
---------------------------------------
总成本：¥0.39
```

---

## 📊 模型选择

### 超低价（推荐）
- **sora-2**: ¥0.030/次 - 最便宜，OpenAI 技术
- **sora-2-all**: ¥0.060/次 - sora-2 逆向版本

### 高性价比
- **veo_3_1-fast**: ¥0.078/次 - Google 快速版
- **grok-video-3**: ¥0.100/次 - Grok 最新

### 高质量（贵）
- **veo3.1**: ¥0.350/次
- **veo3.1-pro**: ¥1.750/次 - 超高质量

修改模型：
```bash
export AI_MODEL=veo_3_1-fast  # 或其他模型
```

---

## ⏰ 推荐的测试时间

为避免 429 错误，建议在以下时间测试：

1. **凌晨时段**（2:00 - 6:00）- 负载最低
2. **工作日上午**（9:00 - 11:00）- 负载适中
3. **周末**- 整体负载较低

---

## 🔍 检查服务器状态

在运行前，先测试一下：

```bash
python3 scripts/vectorengine_client.py \
  --api-key "sk-hSsIao5zgH3uctxxJqWZOezaSW2HZWFTf8HHJQgL6mav6cpJ" \
  --image "storyboards/文脉薪传/keyframes/scene_01_opening_keyframe.png" \
  --prompt "测试视频生成" \
  --model "sora-2" \
  --output "test.mp4"
```

如果返回 429 错误，说明服务器仍在高峰期，请稍后再试。

---

## 📁 输出位置

AI 生成的视频会保存到：

```
storyboards/文脉薪传/dynamic_videos_ve/
├── videos/          # 最终视频（带音频、字幕）
├── audio/           # 生成的音频文件
├── ai_cache/        # AI 生成的视频缓存（重要！避免重复生成）
└── temp/            # 临时文件
```

**注意**：`ai_cache/` 目录中的文件会被自动复用，避免重复调用 API 产生费用。

---

## 🎬 生成完成后

AI 视频生成完成后，需要重新合并：

```bash
cd storyboards/文脉薪传/dynamic_videos_ve/videos

# 创建合并列表
for f in scene_*.mp4; do echo "file '$f'"; done > merge_list.txt

# 合并视频
ffmpeg -y -f concat -safe 0 -i merge_list.txt -c copy "../../文脉薪传_AI完整版.mp4"
```

---

## 💡 提示

1. **缓存机制**：已生成的视频会缓存在 `ai_cache/` 目录，不会重复生成
2. **自动回退**：如果 AI 生成失败，会自动使用 Ken Burns 效果
3. **混合方案**：可以部分场景用 AI，部分用 Ken Burns，平衡成本和质量

---

## 📞 遇到问题？

常见问题排查：

1. **429 错误** → 等待服务器负载降低，或换其他模型
2. **API Key 无效** → 检查环境变量是否正确设置
3. **视频生成失败** → 检查网络连接，查看详细错误日志

---

**祝你创作愉快！** 🎬✨
