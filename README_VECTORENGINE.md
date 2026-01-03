# VectorEngine (向量引擎) 动态视频生成 - 快速指南

使用**最便宜的 sora-2 模型**（¥0.030/次）将静态图片转换为动态视频！

---

## 🎯 为什么选择 VectorEngine + sora-2？

| 对比项 | VectorEngine sora-2 | Google VEO3 | 其他方案 |
|--------|---------------------|-------------|----------|
| **价格** | **¥0.030/次** 🏆 | ¥0.150-1.750/次 | ¥0.06-2.00/次 |
| **质量** | OpenAI最新，物理精准 | Google官方，质量极高 | 各有特色 |
| **速度** | 快速 | 2-5分钟 | 1-3分钟 |
| **配置** | 仅需API Key | 需要GCS+认证 | 各不相同 |
| **成本优势** | **最便宜，是VEO3的1/5** | 昂贵 | 中等 |

## 📦 安装依赖

```bash
pip install requests edge-tts pyyaml
```

## 🚀 快速开始

### 步骤 1: 设置 API Key

```bash
# 设置环境变量
export VECTORENGINE_API_KEY="你的API密钥"

# 可选：设置模型（默认sora-2）
export AI_MODEL="sora-2"  # 或 veo_3_1-fast, grok-video-3

# 可选：是否启用AI（默认启用）
export USE_AI="true"
```

### 步骤 2: 运行生成

```bash
cd /Users/wujames/cursor_prj/wanli-qingyun-project

# 运行混合方案生成（关键分镜用AI，普通分镜用Ken Burns）
python3 scripts/generate_dynamic_videos_vectorengine.py
```

### 步骤 3: 等待完成

脚本会：
1. 自动识别关键分镜
2. 关键分镜使用 sora-2 生成（¥0.030/次）
3. 普通分镜使用 Ken Burns 效果（免费）
4. 添加画外音和字幕
5. 输出完整视频

---

## 📊 成本估算

假设有 20 个场景，其中 5 个关键分镜：

```
关键分镜：5 个 × ¥0.030 = ¥0.15
普通分镜：15 个 × ¥0 (Ken Burns) = ¥0
-------------------------------------
总成本：¥0.15
```

对比 VEO3：
```
关键分镜：5 个 × ¥0.150 = ¥0.75
-------------------------------------
节省：¥0.60 (80%成本节省！)
```

---

## 🎬 可用的 AI 模型

根据你的预算和需求选择：

### 超低价（推荐）
```bash
export AI_MODEL="sora-2"              # ¥0.030/次 - 最便宜！
export AI_MODEL="sora-2-all"          # ¥0.060/次 - sora-2逆向
```

### 高性价比
```bash
export AI_MODEL="veo_3_1-fast"        # ¥0.078/次 - Google快速版
export AI_MODEL="grok-video-3"        # ¥0.100/次 - Grok最新
export AI_MODEL="veo_3_1"             # ¥0.150/次 - Google标准
```

### 高质量（贵）
```bash
export AI_MODEL="veo3.1"              # ¥0.350/次
export AI_MODEL="veo3.1-pro"          # ¥1.750/次 - 超高质量
```

---

## 🛠️ 高级用法

### 1. 仅本地处理（完全免费）

```bash
export USE_AI="false"
python3 scripts/generate_dynamic_videos_vectorengine.py
```

### 2. 全部使用 AI（质量最高但成本最高）

编辑脚本中的 `is_key_scene()` 方法：

```python
def is_key_scene(self, scene: Dict) -> bool:
    """所有场景都使用AI"""
    return True  # 强制所有场景使用AI
```

### 3. 自定义关键分镜规则

```python
def is_key_scene(self, scene: Dict) -> bool:
    """自定义判断逻辑"""
    # 只有特定场景使用AI
    key_scenes = ['scene_01', 'scene_05', 'scene_10']
    return scene['id'] in key_scenes
```

### 4. 测试单张图片

```bash
python3 scripts/vectorengine_client.py \
  --api-key "your-api-key" \
  --image "path/to/image.png" \
  --prompt "描述你想要的动态效果" \
  --model "sora-2" \
  --output "output.mp4"
```

---

## ⚠️ 常见问题

### Q1: 429错误 - 请求过多

**错误信息**：
```
429 Client Error: Too Many Requests
当前分组上游负载已饱和，请稍后再试
```

**解决方案**：
1. **等待几分钟再试**（服务器负载高峰期）
2. 添加重试逻辑
3. 降低并发请求数
4. 选择其他模型（如 veo_3_1-fast）

### Q2: API Key 无效

检查环境变量：
```bash
echo $VECTORENGINE_API_KEY
```

确保 API Key 正确：
```bash
export VECTORENGINE_API_KEY="sk-开头的完整密钥"
```

### Q3: 视频生成失败自动回退

脚本会自动：
1. 如果 AI 生成失败 → 自动使用 Ken Burns
2. 如果 API 不可用 → 全部使用 Ken Burns
3. 保证视频一定能生成

### Q4: 如何查看余额？

```bash
python3 scripts/vectorengine_client.py \
  --api-key "your-api-key" \
  --check-balance
```

---

## 📝 脚本文件说明

### 主要文件

1. **[vectorengine_client.py](scripts/vectorengine_client.py)**
   - VectorEngine API 客户端
   - 支持图生视频和文生视频
   - 包含测试功能

2. **[generate_dynamic_videos_vectorengine.py](scripts/generate_dynamic_videos_vectorengine.py)**
   - 混合方案视频生成器
   - 智能识别关键分镜
   - 自动添加音频和字幕

### 输出目录结构

```
storyboards/文脉薪传/dynamic_videos_ve/
├── videos/          # 最终视频（带音频、字幕）
├── audio/           # 生成的音频文件
├── ai_cache/        # AI生成的视频缓存
└── temp/            # 临时文件
```

---

## 🔍 调试技巧

### 查看详细日志

脚本会打印每个步骤的进度：
```
🎬 场景 1/20: scene_01
   ⏱️  时长: 5秒
   📝 描述: 壮丽的山河全景...
   🔑 关键分镜 - 使用 AI (sora-2)
   🤖 调用 VectorEngine sora-2 生成视频...
   ✅ 视频生成成功
   📝 添加字幕...
   🎵 合并音频...
   ✅ 完成: scene_01.mp4
```

### 测试 API 连接

```bash
# 简单测试
python3 -c "
from vectorengine_client import VectorEngineClient
client = VectorEngineClient(api_key='your-key')
print('API 连接成功！')
"
```

---

## 💡 优化建议

### 成本优化
1. ✅ 使用 sora-2（最便宜）
2. ✅ 只对关键分镜使用 AI
3. ✅ 降低关键分镜识别阈值（时长从4秒提高到6秒）
4. ✅ 利用缓存（AI生成的视频会自动缓存）

### 质量优化
1. 使用更高质量的模型（veo3.1-pro）
2. 提供更详细的提示词
3. 增加视频时长
4. 提高关键帧图片分辨率

### 速度优化
1. 使用快速模型（sora-2, veo_3_1-fast）
2. 并行处理多个场景（需修改脚本）
3. 本地处理普通分镜

---

## 📊 性能对比表

| 方案 | 质量 | 速度 | 成本/20个场景 | 适用场景 |
|------|------|------|---------------|----------|
| 纯 Ken Burns | ⭐⭐⭐ | ⚡⚡⚡ | ¥0 | 快速预览、demo |
| 混合 sora-2 | ⭐⭐⭐⭐ | ⚡⚡ | **¥0.15** | **推荐！日常使用** |
| 混合 veo3.1 | ⭐⭐⭐⭐ | ⚡⚡ | ¥0.75 | 高质量需求 |
| 全 sora-2 | ⭐⭐⭐⭐⭐ | ⚡ | ¥0.60 | 专业作品 |
| 全 veo3.1-pro | ⭐⭐⭐⭐⭐ | ⚡ | ¥35.00 | 影视级质量 |

---

## 🔗 相关资源

- **VectorEngine 官网**: https://api.vectorengine.ai/
- **价格表**: 你之前提供的页面
- **备用方案**: [README_DYNAMIC_VIDEO.md](README_DYNAMIC_VIDEO.md) (使用 Google VEO3)

---

## 📅 下次服务器不繁忙时测试

由于当前遇到 429 错误（服务器负载高），建议：

1. **稍后再试**（建议凌晨或工作日上午）
2. **先用 Ken Burns** 预览效果
3. **测试完成后**再大规模生成

---

## 🎉 总结

使用 VectorEngine 的 sora-2 模型：
- ✅ **成本最低**：¥0.030/次，是市场价的 1/5
- ✅ **质量保证**：OpenAI 最新技术
- ✅ **配置简单**：只需 API Key
- ✅ **自动回退**：失败自动使用 Ken Burns
- ✅ **混合方案**：平衡成本和质量

**开始使用**：
```bash
export VECTORENGINE_API_KEY="sk-hSsIao5zgH3uctxxJqWZOezaSW2HZWFTf8HHJQgL6mav6cpJ"
python3 scripts/generate_dynamic_videos_vectorengine.py
```

祝你创作愉快！🎬✨
