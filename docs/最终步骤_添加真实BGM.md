# 🎵 最终步骤：为视频添加真实中国风BGM

## ✅ 当前状态

- **演示视频已生成**：`storyboards/文脉薪传/文脉薪传_带演示BGM.mp4`
  - 包含演示音效（简单音调）
  - 用于验证BGM添加功能正常工作

## 🎯 下一步：替换为真实中国风BGM

### 方案A：快速获取（推荐）- Pixabay Music

1. **访问Pixabay Music（无需登录，完全免费）**
   ```
   https://pixabay.com/music/search/chinese/
   ```

2. **推荐曲目**（直接点击下载）：

   | 曲目名称 | 风格 | 时长 | 下载链接 |
   |---------|------|------|---------|
   | Chinese Meditation | 古筝 | 2:30 | 点击"Free Download" |
   | Traditional Bamboo Flute | 笛子 | 3:00 | 点击"Free Download" |
   | Guzheng Serenity | 古筝 | 2:45 | 点击"Free Download" |
   | Ancient China | 传统乐器 | 3:15 | 点击"Free Download" |

3. **下载步骤**：
   - 点击任一曲目进入详情页
   - 点击绿色"Free Download"按钮
   - 选择MP3格式
   - 下载到电脑

4. **放置BGM文件**：
   ```bash
   # 将下载的文件重命名并移动到BGM目录
   mv ~/Downloads/你下载的文件名.mp3 storyboards/文脉薪传/bgm/traditional_chinese.mp3
   ```

5. **添加BGM到视频**：
   ```bash
   source venv/bin/activate

   python add_bgm_to_video.py \
     --video "storyboards/文脉薪传/文脉薪传_完整版.mp4" \
     --bgm "storyboards/文脉薪传/bgm/traditional_chinese.mp3" \
     --output "storyboards/文脉薪传/文脉薪传_最终版.mp4" \
     --volume 0.12
   ```

---

### 方案B：YouTube Audio Library

1. **访问YouTube Audio Library**（需要Google账号）
   ```
   https://studio.youtube.com/channel/UC_YOUR_CHANNEL/music
   ```

2. **筛选步骤**：
   - Genre → World & Traditional
   - Mood → Calm 或 Dramatic
   - 搜索关键词：chinese, asian, zen

3. **下载并添加**（同方案A的步骤4-5）

---

### 方案C：Epidemic Sound（专业音乐库）

访问：https://www.epidemicsound.com/music/search/?term=chinese%20traditional

需要订阅，但提供高质量专业音乐。

---

## 🎼 BGM选择建议

根据"文脉薪传"主题，推荐以下特点的音乐：

### ✅ 推荐特点：
- **乐器**：古筝、琵琶、二胡、笛子
- **节奏**：舒缓、悠扬
- **情绪**：庄重、优雅、富有文化底蕴
- **时长**：2-4分钟（会自动循环）

### ❌ 避免：
- 节奏过快的现代电子音乐
- 过于欢快的流行音乐
- 西方古典音乐

---

## 🔧 音量调整指南

根据试听效果调整`--volume`参数：

| BGM感受 | 建议音量值 | 说明 |
|---------|-----------|------|
| 太响，盖过解说 | 0.08 - 0.10 | 降低音量 |
| **刚刚好** | **0.12 - 0.15** | **推荐值** |
| 太轻，几乎听不到 | 0.18 - 0.20 | 提高音量 |

**重新生成命令**（调整音量后）：
```bash
python add_bgm_to_video.py \
  --video "storyboards/文脉薪传/文脉薪传_完整版.mp4" \
  --bgm "storyboards/文脉薪传/bgm/traditional_chinese.mp3" \
  --output "storyboards/文脉薪传/文脉薪传_最终版.mp4" \
  --volume 0.15  # 修改这里
```

---

## 📋 完整操作流程

```bash
# 1. 下载BGM（从Pixabay等网站）
# 假设下载的文件是：Chinese-Meditation.mp3

# 2. 移动文件到BGM目录
mv ~/Downloads/Chinese-Meditation.mp3 storyboards/文脉薪传/bgm/traditional_chinese.mp3

# 3. 激活虚拟环境
source venv/bin/activate

# 4. 添加BGM到视频
python add_bgm_to_video.py \
  --video "storyboards/文脉薪传/文脉薪传_完整版.mp4" \
  --bgm "storyboards/文脉薪传/bgm/traditional_chinese.mp3" \
  --output "storyboards/文脉薪传/文脉薪传_最终版.mp4" \
  --volume 0.12

# 5. 查看输出文件
ls -lh "storyboards/文脉薪传/文脉薪传_最终版.mp4"

# 6. 播放查看效果
open "storyboards/文脉薪传/文脉薪传_最终版.mp4"

# 7. 如果音量不合适，重新调整volume参数并重新运行步骤4
```

---

## 🎥 输出文件说明

执行完成后，您将得到：

| 文件名 | 说明 |
|--------|------|
| `文脉薪传_完整版.mp4` | 原始视频（仅画外音） |
| `文脉薪传_带演示BGM.mp4` | 演示版本（简单音调BGM） |
| `文脉薪传_最终版.mp4` | **最终版本（真实中国风BGM）** |

---

## ⭐ 快速链接

- **Pixabay中国风音乐搜索**：https://pixabay.com/music/search/chinese/
- **Pixabay古筝音乐搜索**：https://pixabay.com/music/search/guzheng/
- **Pixabay冥想音乐搜索**：https://pixabay.com/music/search/meditation%20asian/

---

## ✅ 项目完成检查清单

- [x] 13个场景脚本编写
- [x] 26张AI图片生成（开始帧+关键帧）
- [x] 13个场景视频生成（画外音+字幕）
- [x] 视频合并完成
- [x] 字幕显示修复
- [x] BGM添加功能验证
- [ ] **下载真实中国风BGM** ← 您的下一步
- [ ] **生成最终版视频**

---

祝您创作顺利！ 🎬

制作时间：2025年12月31日
