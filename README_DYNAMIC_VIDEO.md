# 动态视频生成系统 - 使用指南

这是一个**混合方案**的视频生成系统，能够将静态图片转换为动态视频：
- **关键分镜**：使用 Google VEO3 AI 生成真实动态视频
- **普通分镜**：使用增强版 Ken Burns 效果（缩放、平移）

## 📋 目录

- [功能特性](#功能特性)
- [安装配置](#安装配置)
- [快速开始](#快速开始)
- [高级用法](#高级用法)
- [常见问题](#常见问题)

---

## ✨ 功能特性

### 1. 智能分镜识别
自动识别哪些分镜需要使用AI生成：
- 场景标记为 `key: true`
- 场景时长 ≥ 4秒
- 场景描述包含动作词汇（飞行、移动、旋转等）

### 2. VEO3 AI 视频生成
- 使用 Google Veo 3.1 生成高质量动态视频
- 支持从图片生成视频（image-to-video）
- 自动上传/下载到 Google Cloud Storage

### 3. Ken Burns 效果
为普通分镜添加专业的动态效果：
- `zoom_in` - 缓慢放大
- `zoom_out` - 缓慢缩小
- `pan_left` - 向左平移
- `pan_right` - 向右平移
- `diagonal` - 对角线移动

### 4. 完整视频制作
- 自动生成画外音（使用 edge-tts）
- 添加字幕到视频
- 合并音频和视频
- 生成最终完整视频

---

## 🔧 安装配置

### 步骤 1: 安装 Python 依赖

```bash
pip install google-genai google-cloud-storage edge-tts pyyaml
```

### 步骤 2: 安装系统依赖

确保已安装 FFmpeg：

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# 从 https://ffmpeg.org/download.html 下载
```

### 步骤 3: 配置 Google Cloud（仅使用 VEO3 时需要）

#### 3.1 创建 Google Cloud 项目

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 Vertex AI API

#### 3.2 设置认证

```bash
# 安装 gcloud CLI
# https://cloud.google.com/sdk/docs/install

# 登录认证
gcloud auth application-default login

# 设置项目
gcloud config set project YOUR_PROJECT_ID
```

#### 3.3 创建 Cloud Storage Bucket

```bash
# 创建 bucket
gcloud storage buckets create gs://your-bucket-name \
  --location=us-central1

# 或在控制台创建:
# https://console.cloud.google.com/storage
```

#### 3.4 设置环境变量

创建 `.env` 文件或导出环境变量：

```bash
# Google Cloud 配置
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="global"
export GOOGLE_GENAI_USE_VERTEXAI=True

# GCS Bucket 配置
export GCS_BUCKET="gs://your-bucket-name/video-project"

# 是否启用 VEO3（可选，默认为 true）
export USE_VEO="true"
```

#### 3.5 验证配置

```bash
# 运行配置检查
python scripts/gcs_utils.py setup
```

预期输出：
```
✅ 检测到Google Cloud配置:
   项目ID: your-project-id
   位置: global
   认证: ✅ 成功
```

---

## 🚀 快速开始

### 方式 1: 仅使用本地 Ken Burns 效果（不需要 VEO3）

适合快速测试或不需要 AI 生成的场景。

```bash
# 禁用 VEO3
export USE_VEO="false"

# 运行生成
python scripts/generate_dynamic_videos.py
```

**优点**：
- ✅ 完全免费
- ✅ 无需 Google Cloud 账号
- ✅ 速度快

**缺点**：
- ❌ 效果相对简单（仅缩放和平移）
- ❌ 无真实动态效果

### 方式 2: 使用混合方案（推荐）

关键分镜使用 VEO3，普通分镜使用 Ken Burns。

```bash
# 1. 设置环境变量（见上方配置部分）
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GCS_BUCKET="gs://your-bucket-name/prefix"
export USE_VEO="true"

# 2. 运行生成
python scripts/generate_dynamic_videos.py
```

**优点**：
- ✅ 关键分镜质量极高
- ✅ 成本可控（仅关键分镜使用 AI）
- ✅ 自动智能选择

**缺点**：
- ⚠️ 需要 Google Cloud 账号
- ⚠️ VEO3 生成较慢（每个视频约 2-5 分钟）

### 方式 3: 全部使用 VEO3

所有分镜都使用 AI 生成（质量最高但成本最高）。

修改脚本中的 `is_key_scene()` 方法：

```python
def is_key_scene(self, scene: Dict) -> bool:
    """所有场景都使用VEO3"""
    return True  # 强制所有场景使用AI
```

---

## 📂 项目结构

```
wanli-qingyun-project/
├── scripts/
│   ├── generate_dynamic_videos.py    # 主生成脚本
│   ├── gcs_utils.py                  # GCS 工具
│   ├── generate_scene_videos.py      # 旧版本（静态）
│   └── generate_scene_videos_with_narration.py
├── 文脉薪传_细化脚本.yaml              # 场景脚本
└── storyboards/文脉薪传/
    ├── doubao_images/                # 起始帧图片
    ├── keyframes/                    # 关键帧图片
    └── dynamic_videos/               # 输出目录
        ├── videos/                   # 最终视频
        ├── audio/                    # 音频文件
        ├── veo_cache/                # VEO3 缓存
        └── temp/                     # 临时文件
```

---

## 🎯 高级用法

### 1. 自定义关键分镜判断逻辑

编辑 `generate_dynamic_videos.py` 中的 `is_key_scene()` 方法：

```python
def is_key_scene(self, scene: Dict) -> bool:
    """自定义判断逻辑"""
    # 示例：只有特定ID的场景使用VEO3
    key_scene_ids = ['scene_01', 'scene_05', 'scene_10']
    if scene['id'] in key_scene_ids:
        return True

    # 或：基于场景类型
    if scene.get('type') == 'climax':
        return True

    return False
```

### 2. 自定义 Ken Burns 效果

修改 `create_scene_video()` 中的效果选择：

```python
# 方案1: 随机效果
import random
effects = ["zoom_in", "zoom_out", "pan_right", "pan_left", "diagonal"]
effect = random.choice(effects)

# 方案2: 根据场景内容
if '天空' in description:
    effect = "zoom_in"
elif '人物' in description:
    effect = "pan_right"
else:
    effect = "diagonal"
```

### 3. 批量上传图片到 GCS

```bash
# 使用 GCS 工具批量上传
python scripts/gcs_utils.py upload \
  --bucket your-bucket-name \
  --local-path ./storyboards/文脉薪传/keyframes \
  --gcs-path video-project/images
```

### 4. 自定义 VEO3 提示词

编辑 `create_scene_video()` 中的提示词生成：

```python
# 更详细的提示词
veo_prompt = f"""
场景描述：{description}
动作要求：画面需要有自然流畅的动态效果
风格：电影级质感，光影变化自然
镜头运动：缓慢推进
"""
```

---

## 🎬 脚本文件格式

YAML 脚本文件示例：

```yaml
project:
  title: "文脉薪传"
  voice: "zh-CN-YunxiNeural"  # edge-tts 语音

scenes:
  - id: "scene_01"
    duration: 5
    key: true  # 标记为关键分镜（使用 VEO3）
    description: "壮丽的山河全景，云雾缭绕"
    narration: "中华文明，源远流长。"

  - id: "scene_02"
    duration: 3
    description: "书法特写"
    narration: "五千年文化，薪火相传。"
    # key 未设置，会根据时长和内容自动判断
```

---

## ❓ 常见问题

### Q1: VEO3 初始化失败

**错误信息**：
```
⚠️  VEO3 初始化失败: ...
```

**解决方案**：
1. 检查环境变量是否正确设置
   ```bash
   echo $GOOGLE_CLOUD_PROJECT
   echo $GCS_BUCKET
   ```

2. 验证认证状态
   ```bash
   gcloud auth application-default print-access-token
   ```

3. 确认 Vertex AI API 已启用
   ```bash
   gcloud services enable aiplatform.googleapis.com
   ```

### Q2: VEO3 生成超时

VEO3 生成一个视频可能需要 2-5 分钟。如果超时：

1. 检查脚本中的超时设置（默认 30 分钟）
2. 在 Google Cloud Console 查看 Vertex AI 作业状态
3. 检查 GCS bucket 权限

### Q3: 成本控制

VEO3 定价参考（以 Google Cloud 官方为准）：
- 约 $0.05/秒 视频

**节省成本建议**：
1. 仅关键分镜使用 VEO3
2. 降低关键分镜识别阈值
3. 使用缓存（脚本会自动缓存已生成视频）

### Q4: Ken Burns 效果不够平滑

调整 FFmpeg 参数：

```python
# 增加帧率
'-r', '60',  # 从 30 改为 60

# 调整缩放速度
"zoompan=z='min(zoom+0.0005,1.3)'"  # 从 0.001 改为 0.0005
```

### Q5: 字幕显示问题

**问题**：字幕不显示或乱码

**解决**：
1. 确认字体文件路径（macOS 使用 PingFang.ttc）
2. Windows 用户修改为：
   ```python
   fontfile = 'C:/Windows/Fonts/msyh.ttc'  # 微软雅黑
   ```

3. Linux 用户修改为：
   ```python
   fontfile = '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc'
   ```

---

## 📊 性能对比

| 方案 | 质量 | 速度 | 成本 | 适用场景 |
|------|------|------|------|----------|
| 纯 Ken Burns | ⭐⭐⭐ | ⚡⚡⚡ | 免费 | 快速原型、预览 |
| 混合方案（推荐） | ⭐⭐⭐⭐ | ⚡⚡ | 中等 | 正式作品、平衡质量和成本 |
| 全 VEO3 | ⭐⭐⭐⭐⭐ | ⚡ | 较高 | 高质量展示、关键场景 |

---

## 🔗 相关资源

- **Google Veo 文档**: [Vertex AI Video Generation](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/video/overview)
- **Google Cloud Storage**: [GCS Documentation](https://cloud.google.com/storage/docs)
- **Edge-TTS**: [GitHub Repo](https://github.com/rany2/edge-tts)
- **FFmpeg 文档**: [FFmpeg Filters](https://ffmpeg.org/ffmpeg-filters.html)

---

## 📝 更新日志

### v2.0 - 2026-01-02
- ✨ 新增 VEO3 AI 视频生成支持
- ✨ 新增智能分镜识别
- ✨ 新增混合方案架构
- ✨ 新增 5 种 Ken Burns 效果
- ✨ 新增 GCS 工具类
- 🐛 修复字幕显示问题

### v1.0
- 基础静态图片过渡

---

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**祝你创作愉快！** 🎬✨
