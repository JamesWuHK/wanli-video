# AI 图像生成指南

本文档介绍如何为"文脉薪传"项目的13个场景生成 AI 设计图。

---

## 🎯 快速开始（推荐方案）

### 方案一：使用 Replicate (最简单⭐⭐⭐)

**成本**: 约 $0.07-0.15 (13张图)
**时间**: 10-20分钟
**质量**: ⭐⭐⭐⭐⭐

#### 步骤：

1. **注册 Replicate**
   ```
   访问: https://replicate.com/
   点击 "Sign up" 注册账号
   ```

2. **获取 API Token**
   ```
   登录后访问: https://replicate.com/account/api-tokens
   点击 "Create token" 创建新令牌
   复制 token (格式: r8_xxxxx...)
   ```

3. **配置环境变量**
   ```bash
   # 在 .env 文件中添加
   echo "REPLICATE_API_TOKEN=your_token_here" >> .env

   # 或者直接导出
   export REPLICATE_API_TOKEN=your_token_here
   ```

4. **安装依赖并运行**
   ```bash
   cd /Users/wujames/cursor_prj/demo-video-generator
   source venv/bin/activate

   # 使用 FLUX 模型生成（推荐）
   python generate_images_replicate.py \
     --script 文脉薪传_细化脚本.yaml \
     --output storyboards/文脉薪传/ai_images \
     --model flux-schnell
   ```

5. **查看结果**
   ```bash
   open storyboards/文脉薪传/ai_images/
   ```

---

## 📊 API 服务对比

| 服务 | 价格/张 | 速度 | 质量 | 难度 | 推荐度 |
|------|---------|------|------|------|--------|
| **Replicate** | $0.006 | 快 | ⭐⭐⭐⭐⭐ | 简单 | ⭐⭐⭐⭐⭐ |
| **通义万相** | ¥0.08 | 很快 | ⭐⭐⭐⭐ | 简单 | ⭐⭐⭐⭐ |
| **Stability AI** | $0.002 | 中等 | ⭐⭐⭐⭐ | 中等 | ⭐⭐⭐⭐ |
| **OpenAI DALL-E 3** | $0.04 | 中等 | ⭐⭐⭐⭐⭐ | 简单 | ⭐⭐⭐ |
| **Midjourney** | $10/月 | 慢 | ⭐⭐⭐⭐⭐ | 手动 | ⭐⭐⭐ |

---

## 🚀 详细方案

### 方案二：使用通义万相（国内推荐）

**优势**: 国内访问快、中文支持好、价格便宜

#### 步骤：

1. **开通服务**
   ```
   访问: https://dashscope.aliyun.com/
   登录阿里云账号
   开通"通义万相"服务
   ```

2. **获取 API Key**
   ```
   进入控制台 > API Key 管理
   创建新的 API Key
   ```

3. **安装 SDK**
   ```bash
   pip install dashscope
   ```

4. **运行生成**（我可以为您创建专用脚本）

### 方案三：使用 Stability AI

**优势**: 价格最便宜、可自定义参数

#### 步骤：

1. **注册账号**
   ```
   访问: https://platform.stability.ai/
   ```

2. **获取 API Key**
   ```
   Dashboard > API Keys > Create
   ```

3. **安装 SDK**
   ```bash
   pip install stability-sdk
   ```

4. **运行生成**

### 方案四：手动使用 Midjourney（最高质量）

**优势**: 图像质量最好、艺术性最强

#### 步骤：

1. **订阅 Midjourney**
   ```
   访问: https://www.midjourney.com/
   选择订阅计划（Basic $10/月）
   ```

2. **加入 Discord**
   ```
   在 Discord 中加入 Midjourney 服务器
   ```

3. **使用提示词**
   ```
   在脚本中已经为每个场景准备了专业英文提示词
   复制提示词到 Discord
   输入: /imagine prompt: [粘贴提示词]
   ```

4. **下载图片**
   ```
   选择最佳结果
   点击 U1/U2/U3/U4 放大
   保存图片
   ```

---

## 💡 提示词位置

所有场景的 AI 图像生成提示词都在：

**文件**: `文脉薪传_细化脚本.yaml`

**位置**: 每个场景的 `image_generation_prompt` 字段

**示例**:
```yaml
scenes:
  - id: scene_01_opening
    image_generation_prompt: >
      A serene ancient Chinese academy at dawn, warm sunlight streaming through
      traditional wooden lattice windows. An elderly scholar in traditional robes
      opening a yellowed ancient book 'The Analects'. Camera slowly zooms into the
      calligraphy characters '仁义礼智信' written in elegant Chinese brush style.
      Cinematic lighting, ink wash painting aesthetic, warm sepia tones,
      highly detailed, 8K quality.
```

---

## 🎨 模型选择建议

### 对于"文脉薪传"项目：

**推荐模型**: FLUX Schnell 或 SDXL

**原因**:
- 支持复杂的场景描述
- 对中国传统文化元素理解好
- 能生成水墨画风格
- 16:9 宽屏比例

**参数建议**:
```python
{
    "aspect_ratio": "16:9",
    "output_format": "png",
    "output_quality": 90,
    "guidance_scale": 7.5,  # 提示词遵循度
    "num_inference_steps": 30  # 生成质量
}
```

---

## 📝 使用示例

### 完整命令示例：

```bash
# 1. 进入项目目录
cd /Users/wujames/cursor_prj/demo-video-generator

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 设置 API Token（选择一个）
export REPLICATE_API_TOKEN=r8_your_token_here

# 4. 生成图像
python generate_images_replicate.py \
  --script 文脉薪传_细化脚本.yaml \
  --output storyboards/文脉薪传/ai_images \
  --model flux-schnell

# 5. 查看结果
open storyboards/文脉薪传/ai_images/
```

---

## 🔧 故障排除

### 问题1: "需要提供 REPLICATE_API_TOKEN"

**解决**:
```bash
# 检查环境变量
echo $REPLICATE_API_TOKEN

# 如果为空，设置它
export REPLICATE_API_TOKEN=your_token

# 或在命令中直接指定
python generate_images_replicate.py --api-key your_token ...
```

### 问题2: 生成超时

**解决**:
- 网络问题，重试
- 使用更快的模型（flux-schnell）
- 简化提示词

### 问题3: 图像质量不满意

**解决**:
- 尝试不同模型（sdxl, playground-v2.5）
- 调整提示词
- 增加 guidance_scale
- 使用 Midjourney 手动生成

---

## 💰 成本估算

### 生成13张图像的成本：

| 服务 | 单价 | 总成本 | 时间 |
|------|------|--------|------|
| Replicate (FLUX) | $0.006 | **$0.08** | 10-15分钟 |
| Replicate (SDXL) | $0.01 | **$0.13** | 15-20分钟 |
| 通义万相 | ¥0.08 | **¥1.04** | 5-10分钟 |
| DALL-E 3 | $0.04 | **$0.52** | 20-30分钟 |
| Stability AI | $0.002 | **$0.03** | 15-25分钟 |
| Midjourney | $10/月 | **$10** | 1-2小时（手动）|

**推荐**: Replicate (FLUX) - 性价比最高！

---

## 📚 更多资源

### API 文档
- Replicate: https://replicate.com/docs
- 通义万相: https://help.aliyun.com/zh/dashscope/
- Stability AI: https://platform.stability.ai/docs

### 提示词优化
- Prompt Engineering Guide: https://www.promptingguide.ai/
- FLUX Prompt Tips: https://replicate.com/blog/run-flux-schnell

---

## 🎯 下一步

生成图像后：

1. **查看和筛选**
   ```bash
   open storyboards/文脉薪传/ai_images/
   ```

2. **如需重新生成某个场景**
   - 删除对应的图片文件
   - 重新运行脚本（会自动跳过已存在的）

3. **开始视频制作**
   - 使用这些图片作为参考或直接素材
   - 按照《使用指南.md》中的制作路径进行

---

**需要帮助？**

如果您需要：
- 帮助配置 API
- 创建其他服务的生成脚本
- 调整提示词
- 优化生成质量

请随时告诉我！
