# 🎵 如何为视频添加背景音乐（BGM）

## 方法1：手动下载免费BGM（推荐）

### 步骤1：下载免费中国风BGM

从以下网站下载免费的中国传统音乐：

#### 推荐网站：

1. **Pixabay Music**（最推荐，无需登录）
   - 访问：https://pixabay.com/music/search/chinese%20traditional/
   - 搜索关键词：chinese traditional, guzheng, erhu
   - 下载MP3格式

2. **YouTube Audio Library**（需要YouTube账号）
   - 访问：https://www.youtube.com/audiolibrary
   - 筛选：Genre → World & Traditional
   - 搜索：Chinese, Asian

3. **Free Music Archive**
   - 访问：https://freemusicarchive.org/
   - 搜索：chinese traditional

4. **Incompetech**
   - 访问：https://incompetech.com/music/royalty-free/music.html
   - 浏览：World & Traditional

### 步骤2：将BGM文件放入指定目录

```bash
# 将下载的MP3文件移动到BGM目录
mv ~/Downloads/your_bgm_file.mp3 storyboards/文脉薪传/bgm/traditional_chinese.mp3
```

### 步骤3：运行添加BGM脚本

```bash
source venv/bin/activate

python add_bgm_to_video.py \
  --video "storyboards/文脉薪传/文脉薪传_完整版.mp4" \
  --bgm "storyboards/文脉薪传/bgm/traditional_chinese.mp3" \
  --output "storyboards/文脉薪传/文脉薪传_最终版_带BGM.mp4" \
  --volume 0.15
```

**参数说明**：
- `--video`: 输入视频路径
- `--bgm`: 背景音乐文件路径
- `--output`: 输出视频路径
- `--volume`: BGM音量（0.0-1.0），默认0.15（15%）

### 步骤4：调整BGM音量（可选）

如果BGM太大声或太小声，可以调整`--volume`参数：

```bash
# BGM更轻柔（10%）
--volume 0.10

# BGM更响亮（20%）
--volume 0.20
```

---

## 方法2：使用已准备好的脚本

如果您已经有BGM文件并命名为`traditional_chinese.mp3`：

```bash
source venv/bin/activate

# 直接运行（默认参数）
python add_bgm_to_video.py \
  --video "storyboards/文脉薪传/文脉薪传_完整版.mp4" \
  --bgm "storyboards/文脉薪传/bgm/traditional_chinese.mp3" \
  --output "storyboards/文脉薪传/文脉薪传_最终版_带BGM.mp4"
```

---

## 🎼 推荐BGM曲目

适合"文脉薪传"主题的音乐：

1. **古筝独奏**
   - 舒缓、优雅
   - 适合开篇和结尾

2. **琵琶演奏**
   - 情感丰富
   - 适合过渡场景

3. **笛子音乐**
   - 悠扬、深远
   - 适合叙事场景

4. **传统管弦乐**
   - 大气磅礴
   - 适合高潮部分

---

## 📋 完整工作流程示例

```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 检查BGM文件是否存在
ls -lh storyboards/文脉薪传/bgm/

# 3. 添加BGM到视频
python add_bgm_to_video.py \
  --video "storyboards/文脉薪传/文脉薪传_完整版.mp4" \
  --bgm "storyboards/文脉薪传/bgm/traditional_chinese.mp3" \
  --output "storyboards/文脉薪传/文脉薪传_最终版_带BGM.mp4" \
  --volume 0.15

# 4. 检查输出文件
ls -lh "storyboards/文脉薪传/文脉薪传_最终版_带BGM.mp4"

# 5. 播放查看效果
open "storyboards/文脉薪传/文脉薪传_最终版_带BGM.mp4"
```

---

## ⚠️ 注意事项

1. **音频格式**：支持MP3、WAV、AAC等常见格式
2. **音频时长**：BGM会自动循环播放以匹配视频长度
3. **音量平衡**：建议BGM音量设置为0.10-0.20之间
4. **版权问题**：请确保使用的BGM是免费或已获得授权的

---

## 🆘 常见问题

### Q: BGM太大声，盖过了画外音怎么办？
A: 降低`--volume`参数值，例如从0.15降到0.10或0.08

### Q: BGM太小声，几乎听不到？
A: 提高`--volume`参数值，例如从0.15提高到0.20或0.25

### Q: BGM不循环播放？
A: 脚本已经设置了循环播放（`-stream_loop -1`），会自动循环

### Q: 我想要多段BGM？
A: 当前脚本支持单个BGM文件，如需多段BGM，需要修改脚本添加更复杂的音频编辑逻辑

---

制作完成时间：2025年12月31日
